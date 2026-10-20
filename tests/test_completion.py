from pathlib import Path
from src.completion import generate


def test_completion_file_is_up_to_date():
    committed = Path("GroX_complete.bash").read_text()
    assert committed == generate(), "Run: Xvenv/bin/python -m src.completion > ./GroX_complete.bash"