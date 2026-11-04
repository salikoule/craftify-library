import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "client_code" / "CustomComponents" / "TimePicker" / "__init__.py"


def _parse_time():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    func = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "parse_time")
    scope = {}
    exec(compile(ast.Module(body=[func], type_ignores=[]), str(SOURCE), "exec"), scope)
    return scope["parse_time"]


def test_parse_time_accepts_common_shapes():
    parse = _parse_time()
    assert parse("9") == "09:00"
    assert parse("930") == "09:30"
    assert parse("0930") == "09:30"
    assert parse("9:30") == "09:30"
    assert parse("09.30") == "09:30"
    assert parse(" 23:59 ") == "23:59"
    assert parse("") == ""
    assert parse(None) == ""


def test_parse_time_rejects_out_of_range_and_junk():
    parse = _parse_time()
    for text in ("24:00", "12:60", "abc", "12345", "9:305", "-1"):
        assert parse(text) is None
