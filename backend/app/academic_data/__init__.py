from app.config.settings import settings
from app.academic_data.interface import AcademicDataProvider
from app.academic_data.mock import MockAcademicDataProvider
from app.academic_data.external_api import ExternalCollegeAPIProvider

_mock_provider = MockAcademicDataProvider()
_external_provider = ExternalCollegeAPIProvider()


def get_academic_data_provider() -> AcademicDataProvider:
    if settings.ACADEMIC_DATA_PROVIDER.lower() == "external":
        return _external_provider
    return _mock_provider


__all__ = [
    "AcademicDataProvider",
    "MockAcademicDataProvider",
    "ExternalCollegeAPIProvider",
    "get_academic_data_provider",
]
