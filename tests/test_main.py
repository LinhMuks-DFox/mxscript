import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main


def test_driver_exit(tmp_path):
    src = "func main() -> int { return 5; }"
    path = tmp_path / "prog.mxs"
    path.write_text(src)
    result = main.main([str(path)])
    assert result == 5
