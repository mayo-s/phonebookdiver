import logging
from unittest.mock import MagicMock

import pytest

import helper


def test_get_all_collections_hides_geodata_collections() -> None:
    db = MagicMock()
    db.list_collection_names.return_value = ['2005_Q1', 'geodata', 'geodata_not_found', 'geodata_anomalies', '1992_Q2']

    collections = helper.get_all_collections(db)

    assert sorted(collections) == ['1992_Q2', '2005_Q1']


def test_log_linebreak_writes_empty_line(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)

    helper.log('LINEBREAK', 'ignored')

    assert [(r.levelno, r.getMessage()) for r in caplog.records] == [(logging.INFO, '')]


@pytest.mark.parametrize('log_type, level', [('INFO', logging.INFO), ('WARNING', logging.WARNING)])
def test_log_writes_message_with_level(caplog: pytest.LogCaptureFixture, log_type: str, level: int) -> None:
    caplog.set_level(logging.INFO)

    helper.log(log_type, 'Saved to geodata')

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == level
    assert caplog.records[0].getMessage().endswith(' Saved to geodata')
