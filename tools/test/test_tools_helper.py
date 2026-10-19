import importlib.util
import logging
from pathlib import Path
from types import ModuleType

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def tools_helper(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> ModuleType:
    """Loaded by path: api/ has a module named helper too, and this one logs to the working directory on import."""
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location('tools_helper', TOOLS_DIR / 'helper.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_log_linebreak_writes_empty_line(tools_helper: ModuleType, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)

    tools_helper.log('LINEBREAK', 'ignored')

    assert [(r.levelno, r.getMessage()) for r in caplog.records] == [(logging.INFO, '')]


@pytest.mark.parametrize('log_type, level', [('INFO', logging.INFO), ('WARNING', logging.WARNING)])
def test_log_writes_message_with_level(
        tools_helper: ModuleType, caplog: pytest.LogCaptureFixture, log_type: str, level: int) -> None:
    caplog.set_level(logging.INFO)

    tools_helper.log(log_type, 'CONNECTED')

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == level
    assert caplog.records[0].getMessage().endswith(' CONNECTED')
