from unittest.mock import MagicMock

import pytest

import requester

QUERY = {'lastname': 'Schütz'}
SEARCH_RANGE = ['2005_Q1', '2006_Q1']


def entry(_id: int, firstname: str = 'Mario') -> dict:
    return {'_id': _id, 'lastname': 'Schütz', 'firstname': firstname, 'zip': '25899', 'city': 'Niebüll'}


@pytest.fixture
def editions(fake_db: MagicMock) -> dict:
    """Three phone book editions in range; the matches per edition are set by each test."""
    names = ['2005_Q1', '2005_Q2', '2006_Q1']
    fake_db.list_collection_names.return_value = names
    for name in names:
        fake_db[name].count_documents.return_value = 0
        fake_db[name].find.return_value = []
    return {name: fake_db[name] for name in names}


def set_matches(collection: MagicMock, entries: list) -> None:
    collection.count_documents.return_value = len(entries)
    collection.find.return_value = entries


def test_search_colls_counts_matches_with_count_documents(editions: dict) -> None:
    set_matches(editions['2005_Q1'], [entry(1)])

    requester.search_colls(SEARCH_RANGE, QUERY)

    for collection in editions.values():
        collection.count_documents.assert_called_once_with(QUERY)


def test_search_colls_skips_editions_without_matches(editions: dict) -> None:
    set_matches(editions['2005_Q1'], [entry(1)])

    requester.search_colls(SEARCH_RANGE, QUERY)

    editions['2005_Q1'].find.assert_called_once_with(QUERY)
    editions['2005_Q2'].find.assert_not_called()
    editions['2006_Q1'].find.assert_not_called()


def test_search_colls_merges_same_entry_from_several_editions(editions: dict) -> None:
    set_matches(editions['2005_Q1'], [entry(1), entry(2, firstname='Anna')])
    set_matches(editions['2006_Q1'], [entry(7)])

    results = requester.search_colls(SEARCH_RANGE, QUERY)

    assert [r['edition'] for r in results] == [['2005_Q11', '2006_Q17'], ['2005_Q12']]


def test_search_colls_reports_total_matches(editions: dict, capsys: pytest.CaptureFixture) -> None:
    set_matches(editions['2005_Q1'], [entry(1), entry(2, firstname='Anna')])
    set_matches(editions['2006_Q1'], [entry(7)])

    requester.search_colls(SEARCH_RANGE, QUERY)

    assert 'Found 3 total results. Returned 2' in capsys.readouterr().out
