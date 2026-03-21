# tests/test_migrate_html.py
from pathlib import Path
from migrate_html import generate_html, generate_html_file


def test_generate_html_contains_structure():
    dimensions = {
        "overworld": {
            "stats": {"total": 100, "delete": 60, "keep": 40},
            "grid": {
                (0, 0): {"delete": False, "inhabited_time": 500},
                (1, 0): {"delete": True, "inhabited_time": 50},
                (0, 1): {"delete": True, "inhabited_time": 0},
            },
        }
    }
    html = generate_html(dimensions, query="InhabitedTime < 120")
    assert "<!DOCTYPE html>" in html
    assert "InhabitedTime" in html
    assert "canvas" in html.lower()
    assert "Overworld" in html


def test_generate_html_multiple_dimensions():
    dimensions = {
        "overworld": {
            "stats": {"total": 100, "delete": 60, "keep": 40},
            "grid": {(0, 0): {"delete": False, "inhabited_time": 500}},
        },
        "nether": {
            "stats": {"total": 50, "delete": 30, "keep": 20},
            "grid": {(0, 0): {"delete": True, "inhabited_time": 10}},
        },
    }
    html = generate_html(dimensions, query="InhabitedTime < 120")
    assert "Overworld" in html
    assert "Nether" in html


def test_generate_html_writes_file(tmp_path):
    dimensions = {
        "overworld": {
            "stats": {"total": 10, "delete": 5, "keep": 5},
            "grid": {(0, 0): {"delete": False, "inhabited_time": 200}},
        },
    }
    out = tmp_path / "preview.html"
    generate_html_file(dimensions, query="InhabitedTime < 120", output_path=out)
    assert out.exists()
    content = out.read_text()
    assert "<!DOCTYPE html>" in content


def test_generate_html_stats_bar():
    """Stats bar shows totals and delete percentage."""
    dimensions = {
        "overworld": {
            "stats": {"total": 200, "delete": 100, "keep": 100},
            "grid": {},
        }
    }
    html = generate_html(dimensions, query="InhabitedTime < 60")
    # Stats values appear in the HTML
    assert "200" in html
    assert "100" in html
    # Percentage (50.0%)
    assert "50" in html


def test_generate_html_base64_embedded():
    """Chunk data is embedded as base64 in a script tag."""
    dimensions = {
        "overworld": {
            "stats": {"total": 3, "delete": 2, "keep": 1},
            "grid": {
                (0, 0): {"delete": False, "inhabited_time": 1000},
                (1, 0): {"delete": True, "inhabited_time": 10},
                (0, 1): {"delete": True, "inhabited_time": 0},
            },
        }
    }
    html = generate_html(dimensions, query="InhabitedTime < 120")
    # Should have a script tag with base64 data
    assert "<script" in html
    # base64 alphabet characters present (not raw binary)
    import base64
    import re

    # Find base64 blobs in the HTML — look for quoted base64 strings
    b64_matches = re.findall(r'"([A-Za-z0-9+/=]{8,})"', html)
    assert len(b64_matches) > 0, "No base64 data found in HTML"


def test_generate_html_timestamp():
    """HTML includes a timestamp."""
    dimensions = {
        "overworld": {
            "stats": {"total": 1, "delete": 0, "keep": 1},
            "grid": {(0, 0): {"delete": False, "inhabited_time": 500}},
        }
    }
    html = generate_html(dimensions, query="test query")
    # Should contain a year (timestamp)
    import re

    assert re.search(r"202\d", html), "No timestamp year found in HTML"


def test_generate_html_empty_grid():
    """Empty grid is handled without error."""
    dimensions = {
        "overworld": {
            "stats": {"total": 0, "delete": 0, "keep": 0},
            "grid": {},
        }
    }
    html = generate_html(dimensions, query="InhabitedTime < 120")
    assert "<!DOCTYPE html>" in html
    assert "Overworld" in html


def test_generate_html_end_dimension():
    """'end' dimension is displayed as 'End'."""
    dimensions = {
        "end": {
            "stats": {"total": 20, "delete": 18, "keep": 2},
            "grid": {(0, 0): {"delete": True, "inhabited_time": 5}},
        }
    }
    html = generate_html(dimensions, query="InhabitedTime < 120")
    assert "End" in html
