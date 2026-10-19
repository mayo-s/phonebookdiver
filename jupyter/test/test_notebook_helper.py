import importlib.util
import logging
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest

JUPYTER_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def notebook_helper(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Loaded by path: api/ has a module named helper too, and this one logs to ./archive on import."""
    monkeypatch.chdir(JUPYTER_DIR)
    spec = importlib.util.spec_from_file_location('notebook_helper', JUPYTER_DIR / 'helper.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_get_phonebooks_hides_geodata_collections(notebook_helper: ModuleType) -> None:
    db = MagicMock()
    db.list_collection_names.return_value = ['2005_Q1', 'geodata', 'geodata_not_found', '1992_Q2']

    phonebooks = notebook_helper.get_phonebooks(db)

    assert phonebooks == ['1992_Q2', '2005_Q1']


def test_log_linebreak_writes_empty_line(notebook_helper: ModuleType, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)

    notebook_helper.log('LINEBREAK', 'ignored')

    assert [(r.levelno, r.getMessage()) for r in caplog.records] == [(logging.INFO, '')]
