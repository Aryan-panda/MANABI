import logging
from typing import List, Optional
import httpx
from app.academic_data.interface import (
    AcademicDataProvider,
    StudentProfile,
    CourseEnrollment,
    AttendanceRecord,
    ExamResult,
    ClassSchedule,
)
from app.config.settings import settings

logger = logging.getLogger("manabi.academic.external_api")


class ExternalCollegeAPIProvider(AcademicDataProvider):
    """
    Production HTTP adapter for external institutional college APIs.
    Gracefully handles network drops, missing endpoints, and unconfigured credentials.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (base_url or settings.EXTERNAL_COLLEGE_API_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.EXTERNAL_COLLEGE_API_KEY
        self.timeout = 10.0

    def _get_headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def is_configured(self) -> bool:
        return bool(self.base_url)

    async def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        if not self.is_configured():
            logger.info("External college API not configured. Cannot query student profile.")
            return None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/students/{student_id}/profile",
                    headers=self._get_headers(),
                )
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return StudentProfile.model_validate(resp.json())
        except Exception as exc:
            logger.error(f"Failed to fetch student profile from external college API: {exc}")
            return None

    async def get_courses(self, student_id: str) -> List[CourseEnrollment]:
        if not self.is_configured():
            return []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/students/{student_id}/courses",
                    headers=self._get_headers(),
                )
                resp.raise_for_status()
                return [CourseEnrollment.model_validate(c) for c in resp.json()]
        except Exception as exc:
            logger.error(f"Failed to fetch courses from external college API: {exc}")
            return []

    async def get_attendance(self, student_id: str) -> List[AttendanceRecord]:
        if not self.is_configured():
            return []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/students/{student_id}/attendance",
                    headers=self._get_headers(),
                )
                resp.raise_for_status()
                return [AttendanceRecord.model_validate(a) for a in resp.json()]
        except Exception as exc:
            logger.error(f"Failed to fetch attendance from external college API: {exc}")
            return []

    async def get_results(self, student_id: str) -> List[ExamResult]:
        if not self.is_configured():
            return []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/students/{student_id}/results",
                    headers=self._get_headers(),
                )
                resp.raise_for_status()
                return [ExamResult.model_validate(r) for r in resp.json()]
        except Exception as exc:
            logger.error(f"Failed to fetch exam results from external college API: {exc}")
            return []

    async def get_schedule(self, student_id: str) -> List[ClassSchedule]:
        if not self.is_configured():
            return []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/students/{student_id}/schedule",
                    headers=self._get_headers(),
                )
                resp.raise_for_status()
                return [ClassSchedule.model_validate(s) for s in resp.json()]
        except Exception as exc:
            logger.error(f"Failed to fetch schedule from external college API: {exc}")
            return []
