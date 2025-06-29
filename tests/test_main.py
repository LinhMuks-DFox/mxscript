import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

import main


def test_driver_exit(tmp_path):
    src = "func main() -> int { return 5; }"
    path = tmp_path / "prog.mxs"
    path.write_text(src)
    with pytest.raises(SystemExit) as exc:
        main.main([str(path)])
    assert exc.value.code == 5
