import pymongo
import pytest

import requester

# every test in this file talks to the local MongoDB
pytestmark = pytest.mark.integration


def entry(_id: int, firstname: str = 'Mario') -> dict:
    return {'_id': _id, 'lastname': 'Schütz', 'firstname': firstname, 'zip': '25899', 'city': 'Niebüll'}


@pytest.fixture
def editions(mongo_test_db: pymongo.database.Database) -> pymongo.database.Database:
    mongo_test_db['2005_Q1'].insert_many([entry(1), entry(2, firstname='Anna')])
    mongo_test_db['2005_Q2'].insert_one({'_id': 3, 'lastname': 'Meier', 'zip': '25899', 'city': 'Niebüll'})
    mongo_test_db['2006_Q1'].insert_one(entry(7))
    return mongo_test_db


def test_search_colls_finds_and_merges_entries_over_editions(editions: pymongo.database.Database) -> None:
    results = requester.search_colls(['2005_Q1', '2006_Q1'], {'lastname': 'Schütz'})

    assert sorted(r['edition'] for r in results) == [['2005_Q11', '2006_Q17'], ['2005_Q12']]


def test_search_colls_returns_nothing_without_matches(editions: pymongo.database.Database) -> None:
    assert requester.search_colls(['2005_Q1', '2006_Q1'], {'lastname': 'Unknown'}) == []
