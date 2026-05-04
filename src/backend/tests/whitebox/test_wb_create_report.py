from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.models.user import User
from participium.models.report import Report, ReportStatus, ReportPhoto, ReportStatusHistory
from participium.core.exceptions import ValidationError
from participium.services.report_service import ReportService

pytestmark = pytest.mark.whitebox


def _user(*, user_id: int) -> User:
    """Helper per creare un utente fittizio."""
    return User(id=user_id, username="test_citizen")


def _photo(*, filename: str | None = "test.jpg", content_type: str = "image/jpeg") -> Mock:
    """Helper per creare un finto FileStorage."""
    photo = Mock()
    photo.filename = filename
    photo.content_type = content_type
    return photo


@pytest.fixture
def report_service_bundle() -> dict[str, object]:
    session = Mock()
    category_repository = Mock()
    report_repository = Mock()
    storage_service = Mock()
    
    service = ReportService(
        session=session,
        category_repository=category_repository,
        report_repository=report_repository,
        storage_service=storage_service,
    )
    service.get_report = Mock()

    return {
        "service": service,
        "session": session,
        "category_repository": category_repository,
        "report_repository": report_repository,
        "storage_service": storage_service,
    }

# -- TEST CASES --

def test_create_report_raises_when_category_id_is_invalid_format(
    report_service_bundle: dict[str, object],
) -> None:
    service = report_service_bundle["service"]
    reporter = _user(user_id=10)

    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(
            reporter=reporter, category_id="invalid_int", title="T", description="D",
            latitude=45.0, longitude=7.0, photos=[]
        )


def test_create_report_raises_when_category_is_missing(
    report_service_bundle: dict[str, object],
) -> None:
    service = report_service_bundle["service"]
    reporter = _user(user_id=10)

    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(
            reporter=reporter, category_id=None, title="T", description="D",
            latitude=45.0, longitude=7.0, photos=[]
        )


def test_create_report_raises_when_title_or_description_is_missing(
    report_service_bundle: dict[str, object],
) -> None:
    service = report_service_bundle["service"]
    category_repo = report_service_bundle["category_repository"]
    
    category_repo.get_by_id.return_value = Mock(is_active=True)
    reporter = _user(user_id=10)

    with pytest.raises(ValidationError, match="Title and description are required."):
        service.create_report(
            reporter=reporter, category_id=1, title="", description="D",
            latitude=45.0, longitude=7.0, photos=[]
        )


def test_create_report_raises_when_coordinates_are_missing(
    report_service_bundle: dict[str, object],
) -> None:
    service = report_service_bundle["service"]
    category_repo = report_service_bundle["category_repository"]
    
    category_repo.get_by_id.return_value = Mock(is_active=True)
    reporter = _user(user_id=10)

    with pytest.raises(ValidationError, match="Latitude and longitude are required."):
        service.create_report(
            reporter=reporter, category_id=1, title="T", description="D",
            latitude=None, longitude=7.0, photos=[]
        )

def test_create_report_raises_when_coordinates_are_invalid_format(
    report_service_bundle: dict[str, object],
) -> None:
    service = report_service_bundle["service"]
    category_repo = report_service_bundle["category_repository"]
    
    category_repo.get_by_id.return_value = Mock(is_active=True)
    reporter = _user(user_id=10)

    with pytest.raises(ValidationError, match="Latitude and longitude must be valid numbers."):
        service.create_report(
            reporter=reporter, category_id=1, title="T", description="D",
            latitude="invalid_float", longitude=7.0, photos=[]
        )


def test_create_report_raises_when_no_valid_photos_are_provided(
    report_service_bundle: dict[str, object],
) -> None:
    service = report_service_bundle["service"]
    category_repo = report_service_bundle["category_repository"]
    
    category_repo.get_by_id.return_value = Mock(is_active=True)
    reporter = _user(user_id=10)
    
    invalid_photo = _photo(filename=None)

    with pytest.raises(ValidationError, match="At least one photo is required."):
        service.create_report(
            reporter=reporter, category_id=1, title="T", description="D",
            latitude=45.0, longitude=7.0, photos=[invalid_photo]
        )


def test_create_report_raises_when_too_many_photos_are_provided(
    report_service_bundle: dict[str, object],
) -> None:
    service = report_service_bundle["service"]
    category_repo = report_service_bundle["category_repository"]
    
    category_repo.get_by_id.return_value = Mock(is_active=True)
    reporter = _user(user_id=10)
    
    photos = [_photo(filename=f"img{i}.jpg") for i in range(4)]

    with pytest.raises(ValidationError, match="A report can contain at most 3 photos."):
        service.create_report(
            reporter=reporter, category_id=1, title="T", description="D",
            latitude=45.0, longitude=7.0, photos=photos
        )


def test_create_report_persists_successfully_with_valid_data(
    report_service_bundle: dict[str, object],
) -> None:
    service = report_service_bundle["service"]
    session = report_service_bundle["session"]
    category_repo = report_service_bundle["category_repository"]
    report_repo = report_service_bundle["report_repository"]
    storage_service = report_service_bundle["storage_service"]

    category_repo.get_by_id.return_value = Mock(id=99, is_active=True)
    reporter = _user(user_id=10)
    
    photo1 = _photo(filename="buca1.jpg")
    photo2 = _photo(filename="buca2.jpg")
    storage_service.save.side_effect = ["/storage/buca1.jpg", "/storage/buca2.jpg"]
    
    mock_final_report = Mock()
    service.get_report.return_value = mock_final_report

    result = service.create_report(
        reporter=reporter, 
        category_id="99",  
        title="  Tubo Rotto  ", 
        description=" Acqua ",
        latitude="45.1", 
        longitude="7.2",
        photos=[photo1, photo2],
        is_anonymous=True
    )

    assert result == mock_final_report
    
    report_repo.add.assert_called_once()
    saved_report = report_repo.add.call_args[0][0]
    assert saved_report.title == "Tubo Rotto"
    assert saved_report.description == "Acqua"
    assert saved_report.latitude == 45.1
    assert saved_report.category_id == 99
    
    assert storage_service.save.call_count == 2
    assert report_repo.add_photo.call_count == 2
    
    report_repo.add_status_entry.assert_called_once()
    session.flush.assert_called_once()
    session.commit.assert_called_once()