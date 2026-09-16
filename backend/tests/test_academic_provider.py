import pytest
from app.academic_data.mock import MockAcademicDataProvider
from app.academic_data.external_api import ExternalCollegeAPIProvider


@pytest.mark.asyncio
async def test_mock_student_profile():
    provider = MockAcademicDataProvider()
    profile = await provider.get_student_profile("STU1001")
    assert profile is not None
    assert profile.student_id == "STU1001"
    assert profile.full_name == "Aryan Panda"
    assert profile.cgpa == 8.85
    assert profile.academic_status == "Good Standing"


@pytest.mark.asyncio
async def test_mock_attendance_threshold():
    provider = MockAcademicDataProvider()
    attendance = await provider.get_attendance("STU1001")
    assert len(attendance) > 0

    # Verify courses have valid attendance percentages
    for att in attendance:
        assert 0.0 <= att.percentage <= 100.0
        if att.percentage < 75.0 or att.percentage == 75.0:
            assert att.is_critical is True


@pytest.mark.asyncio
async def test_unconfigured_external_api():
    # Empty URL simulates missing external institutional integration
    external_provider = ExternalCollegeAPIProvider(base_url="")
    assert external_provider.is_configured() is False

    profile = await external_provider.get_student_profile("STU9999")
    assert profile is None

    courses = await external_provider.get_courses("STU9999")
    assert courses == []
