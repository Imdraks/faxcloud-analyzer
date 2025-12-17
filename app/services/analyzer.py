import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from statistics import mean, pstdev
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

SUCCESS_STATUSES = {"success", "ok", "sent", "delivered"}


class AnalyzerService:
    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records

    def _is_success(self, status: str) -> bool:
        return status.lower() in SUCCESS_STATUSES

    def compute_stats(self) -> Dict[str, Any]:
        total = len(self.records)
        success_count = sum(1 for r in self.records if self._is_success(r["status"]))
        failed_count = total - success_count
        success_rate = round((success_count / total) * 100, 2) if total else 0.0

        status_counts = Counter(r["status"] for r in self.records)
        error_codes = [r["error_code"] for r in self.records if r.get("error_code")]
        top_error_codes = Counter(error_codes).most_common(10)

        time_series = self._build_time_series()
        anomalies = self._detect_anomalies(time_series, failed_count)

        return {
            "total_transmissions": total,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": success_rate,
            "status_breakdown": dict(status_counts),
            "top_error_codes": top_error_codes,
            "time_series": time_series,
            "anomalies": anomalies,
        }

    def _build_time_series(self) -> List[Dict[str, Any]]:
        grouped = defaultdict(lambda: {"date": None, "success": 0, "failed": 0, "total": 0})
        for r in self.records:
            day = r["sent_at"].strftime("%Y-%m-%d")
            bucket = grouped[day]
            bucket["date"] = day
            bucket["total"] += 1
            if self._is_success(r["status"]):
                bucket["success"] += 1
            else:
                bucket["failed"] += 1
        return sorted(grouped.values(), key=lambda x: x["date"])

    def _detect_anomalies(self, time_series: List[Dict[str, Any]], failed_total: int) -> Dict[str, Any]:
        if len(time_series) < 3:
            return {"failure_spike": None, "dominant_error_code": None}

        failures = [point["failed"] for point in time_series]
        avg = mean(failures)
        sigma = pstdev(failures)
        threshold = avg + 2 * sigma
        spikes = [p for p in time_series if p["failed"] > threshold]

        error_codes = [r["error_code"] for r in self.records if r.get("error_code")]
        code_counter = Counter(error_codes)
        dominant = None
        if failed_total > 0:
            for code, count in code_counter.most_common():
                if (count / failed_total) > 0.2:
                    dominant = {"code": code, "ratio": round((count / failed_total) * 100, 2)}
                    break

        return {
            "failure_spike": spikes[0] if spikes else None,
            "dominant_error_code": dominant,
        }

    @staticmethod
    def stats_json(stats: Dict[str, Any]) -> str:
        return json.dumps(stats, ensure_ascii=False)
