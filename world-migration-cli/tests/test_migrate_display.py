from migrate_display import format_stats_table, format_report, format_safety_abort


def test_format_stats_table_single_dimension():
    stats = [{"dimension": "Overworld", "total": 12847, "delete": 8203, "keep": 4644}]
    table = format_stats_table(stats)
    assert "Overworld" in table
    assert "12,847" in table
    assert "8,203" in table
    assert "63.9%" in table


def test_format_stats_table_multiple_dimensions():
    stats = [
        {"dimension": "Overworld", "total": 12847, "delete": 8203, "keep": 4644},
        {"dimension": "Nether", "total": 2104, "delete": 1456, "keep": 648},
        {"dimension": "End", "total": 891, "delete": 834, "keep": 57},
    ]
    table = format_stats_table(stats)
    assert "Overworld" in table
    assert "Nether" in table
    assert "End" in table
    assert "Total" in table  # aggregate row


def test_format_stats_table_zero_chunks():
    stats = [{"dimension": "End", "total": 0, "delete": 0, "keep": 0}]
    table = format_stats_table(stats)
    assert "0.0%" in table


def test_format_safety_abort():
    msg = format_safety_abort("End", 93.6)
    assert "93.6%" in msg
    assert "End" in msg
    assert "SAFETY ABORT" in msg
    assert "--force" in msg


def test_format_report():
    stats = [
        {"dimension": "Overworld", "total": 100, "delete": 60, "keep": 40},
    ]
    report = format_report(stats, "/tmp/work/world_new", ["overworld"])
    assert "Trim complete" in report
    assert "Overworld" in report
    assert "60" in report
    assert "Next steps" in report
