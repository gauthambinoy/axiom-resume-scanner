from functools import lru_cache

from app.services.scan_service import ScanService


@lru_cache
def get_scan_service() -> ScanService:
    return ScanService()
