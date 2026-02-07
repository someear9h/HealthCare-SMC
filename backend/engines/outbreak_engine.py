from typing import Dict, Any
from core.data_access import DataAccess
import statistics


def detect_outbreaks(storage: DataAccess, record: Dict[str, Any]) -> bool:
    """
    Simple outbreak detection:
    - If total_cases exceeds an absolute threshold
    - Or if total_cases is > 3x the median of the same indicator in recent records
    """
    try:
        threshold = 200
        tc = int(record.get("total_cases", 0))
        if tc >= threshold:
            return True

        # fetch recent records for same indicator and location
        recent = storage.read_last(50)
        same_indicator = [int(r.get("total_cases", 0)) for r in recent if r.get("indicatorname") == record.get("indicatorname")]
        if not same_indicator:
            return False
        med = statistics.median(same_indicator)
        if med == 0:
            return tc > 0
        if tc / med >= 3:
            return True
        return False
    except Exception:
        return False
