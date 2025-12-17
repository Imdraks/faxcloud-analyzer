from app.services.analyzer import AnalyzerService


def test_analyzer_stats():
    records = [
        {"sent_at": __import__("datetime").datetime(2024, 1, 1), "status": "success", "error_code": None},
        {"sent_at": __import__("datetime").datetime(2024, 1, 1), "status": "failed", "error_code": "E1"},
    ]
    analyzer = AnalyzerService(records)
    stats = analyzer.compute_stats()
    assert stats["total_transmissions"] == 2
    assert stats["failed_count"] == 1
    assert stats["top_error_codes"][0][0] == "E1"
