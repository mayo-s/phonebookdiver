"""Finds and fixes wrongly geocoded geodata entries.

    cd api
    pipenv run python -m scripts.geodata_cleanup plan [--report geodata_cleanup_plan.csv]
    pipenv run python -m scripts.geodata_cleanup apply geodata_cleanup_plan.csv

plan only reads geodata and asks Nominatim, apply only executes the reviewed CSV, without new requests.
An entry is wrong if it is more than MAX_KM_TO_SAME_ZIP from its zip's centre (Nominatim, postcode only).
Wrong entries are re-geocoded with postcode + city; if that isn't close to the centre either,
they are moved to geodata_not_found.
"""
import argparse
import csv
from collections import defaultdict

import hm_requester as hm

UPDATE = 'update'
MOVE = 'move to not found'
PLAN_FIELDS = ['zip', 'city', 'old_lat', 'old_lon', 'km_from_centre', 'action', 'new_lat', 'new_lon']


def places_by_zip() -> dict:
    """{zip: {(city, (lat, lon)), ...}} for all real postcodes in geodata."""
    zips = defaultdict(set)
    for doc in hm.db['geodata'].find({}, {'_id': 0, 'zip': 1, 'city': 1, 'coordinates': 1}):
        zip = doc.get('zip')
        if zip and doc.get('coordinates') and hm.is_postcode(zip):
            zips[zip].add((doc.get('city'), tuple(doc['coordinates'])))
    return zips


def is_suspect(places: set) -> bool:
    """True if some place is further than the limit from every other place of the zip."""
    return any(nearest_other_km(city, coords, places) > hm.MAX_KM_TO_SAME_ZIP for city, coords in places)


def nearest_other_km(city: str | None, coords: tuple, places: set) -> float:
    distances = [hm.distance_km(coords, c) for other_city, c in places if other_city != city]
    return min(distances, default=0.0)


def find_suspect_zips(zips: dict) -> list:
    return sorted(zip for zip, places in zips.items() if is_suspect(places))


def first_coords_in_germany(results: list | None) -> list | None:
    coords = hm.parse_nominatim_coords(results or [])
    if coords is None or not hm.in_germany(coords):
        return None
    return coords


def zip_centre(zip: str) -> list | None:
    return first_coords_in_germany(hm.nominatim_search({'postalcode': zip, 'country': 'de', 'format': 'jsonv2'}))


def regeocode(zip: str, city: str, centre: list) -> list | None:
    """Only accepted close to the centre: Nominatim ignores a postcode that doesn't fit the city."""
    params = {'postalcode': zip, 'city': city, 'country': 'de', 'format': 'jsonv2'}
    coords = first_coords_in_germany(hm.nominatim_search(params))
    if coords is None or hm.distance_km(coords, centre) > hm.MAX_KM_TO_SAME_ZIP:
        return None
    return coords


def plan_zip(zip: str, places: set) -> list:
    centre = zip_centre(zip)
    if centre is None:
        print(f'{zip}: no centre from Nominatim, skipped')
        return []
    rows = [plan_entry(zip, city, coords, centre) for city, coords in sorted(places, key=lambda p: (p[0] or '', p[1]))]
    return [row for row in rows if row]


def plan_entry(zip: str, city: str | None, coords: tuple, centre: list) -> dict | None:
    km = hm.distance_km(coords, centre)
    if km <= hm.MAX_KM_TO_SAME_ZIP:
        return None
    new = regeocode(zip, city, centre) if city else None
    row = {'zip': zip, 'city': city or '', 'old_lat': coords[0], 'old_lon': coords[1], 'km_from_centre': round(km),
           'action': MOVE, 'new_lat': '', 'new_lon': ''}
    if new:
        row.update(action=UPDATE, new_lat=new[0], new_lon=new[1])
    return row


def plan(report: str) -> list:
    zips = places_by_zip()
    suspects = find_suspect_zips(zips)
    print(f'{len(suspects)} suspect zips, about {len(suspects)} or more Nominatim requests at 1 per second')
    rows = []
    for i, zip in enumerate(suspects, 1):
        rows.extend(plan_zip(zip, zips[zip]))
        if i % 25 == 0:
            print(f'{i}/{len(suspects)} zips checked, {len(rows)} wrong entries so far')
    write_plan(report, rows)
    print(f'{len(rows)} wrong entries: {sum(r["action"] == UPDATE for r in rows)} to update, '
          f'{sum(r["action"] == MOVE for r in rows)} to move to not found. Plan written to {report}')
    return rows


def write_plan(path: str, rows: list) -> None:
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=PLAN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def read_plan(path: str) -> list:
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def entry_filter(row: dict) -> dict:
    """Matches only entries that still have the planned old coordinates."""
    query = hm.place_query(row['zip'], row['city'] or None)
    query['coordinates'] = [float(row['old_lat']), float(row['old_lon'])]
    return query


def apply_row(row: dict) -> int:
    old = [float(row['old_lat']), float(row['old_lon'])]
    if row['action'] == UPDATE:
        new = [float(row['new_lat']), float(row['new_lon'])]
        return hm.db['geodata'].update_many(entry_filter(row), {'$set': {'coordinates': new}}).modified_count
    if row['action'] == MOVE:
        deleted = hm.db['geodata'].delete_many(entry_filter(row)).deleted_count
        if deleted:
            reason = f'implausible: {row["km_from_centre"]} km from zip centre (cleanup)'
            hm.save_not_found(row['zip'], row['city'] or None, reason=reason, rejected=old)
        return deleted
    raise ValueError(f'Unknown action {row["action"]!r} for {row["zip"]} {row["city"]}')


def apply(path: str) -> int:
    rows = read_plan(path)
    changed = sum(apply_row(row) for row in rows)
    print(f'{len(rows)} planned changes applied, {changed} geodata entries changed')
    return changed


def main(argv: list | None = None) -> None:
    parser = argparse.ArgumentParser(description='Find and fix wrongly geocoded geodata entries.')
    commands = parser.add_subparsers(dest='command', required=True)
    plan_parser = commands.add_parser('plan', help='find wrong entries and write a CSV plan, changes nothing')
    plan_parser.add_argument('--report', default='geodata_cleanup_plan.csv')
    apply_parser = commands.add_parser('apply', help='execute a reviewed CSV plan')
    apply_parser.add_argument('report')
    args = parser.parse_args(argv)
    if args.command == 'plan':
        plan(args.report)
    else:
        apply(args.report)


if __name__ == '__main__':
    main()
