from pathlib import Path

from click.testing import CliRunner
from convcompose import main


def test_xcompose_convert():
    runner = CliRunner()
    file = Path(__file__).parent / 'test.compose'
    result = runner.invoke(main, args=['xcompose', str(file)])
    assert result.exit_code == 0
    assert result.output == '"..": "…"\n'
    result = runner.invoke(main, args=['xcompose', str(file), '--keep-comments'])
    assert result.exit_code == 0
    assert result.output == '"..": "…"  # HORIZONTAL ELLIPSIS\n'
