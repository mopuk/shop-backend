import json

from app.utils.json_loader import load_json


def test_load_json_reads_a_json_file(tmp_path):
    path = tmp_path / "products.json"
    expected = {"products": [{"id": 1, "name": "Example"}]}
    path.write_text(json.dumps(expected), encoding="utf-8")

    assert load_json(path) == expected
