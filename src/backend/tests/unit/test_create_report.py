from __future__ import annotations

from participium.services.report_service import ReportService
from participium.core.exceptions import ValidationError
from participium.models.user import User
from participium.models.category import Category
from participium.models.report import Report, ReportPhoto
import pytest

from dataclasses import field
from participium.models.enums import ReportStatus


# Function: create_report
# Inputs: reporter: User, category_id: int | str | None, title: str | None, description: str | None, latitude: float | str | None, longitude: float | str | None, photos: list[FileStorage], is_anonymous: bool = False
# Expected Output:
# - The created `Report`, reloaded after persistence if successful.
# - ValidationError: if `category_id` is missing, malformed, unknown, or refers to an inactive category.
# - ValidationError: if `title` or `description` is missing.
# - ValidationError: if `latitude` or `longitude` is missing.
# - ValidationError: if coordinates cannot be converted to valid numeric values.
# - ValidationError: if there are no valid uploaded photos.
# - ValidationError: if more than 3 valid photos are provided.
# def create_report(
#   self,
#   reporter: User,
#   category_id: int | str | None,
#   title: str | None,
#   description: str | None,
#   latitude: float | str | None,
#   longitude: float | str | None,
#   photos: list[FileStorage],
#   is_anonymous: bool = False,
#   ) -> Report

CORRECT_USER = User(
    id=102,
    username="luca.bianchi",
    first_name="Luca",
    last_name="Bianchi",
    email="luca.bianchi@example.com",
    password_hash="HASHED_PASSWORD_102",
    is_active=True,
    is_email_verified=True,
)

CORRECT_CATEGORY = Category(
    id=1, name="Waste", is_active= True
)

MALFORMED_CATEGORY = Category(
    id=-1, name="Waste", is_active=True
)

UNKNOWN_CATEGORY = Category(
    id=2, name="Categ", is_active=True
)

INACTIVE_CATEGORY = Category(
    id=3, name="Waste", is_active=False
)

photo_obj = ReportPhoto(file_path="path/to/img.jpg")

CORRECT_REPORT = Report(
    id = None,
    title = "Titolo Valido",
    description = "Descrizione valida",
    latitude = 45.0,
    longitude = 9.0,
    is_anonymous = False,
    status = ReportStatus.PENDING_APPROVAL,
    rejection_reason = None,
    reporter_id = 102,
    category_id = 1,
    reporter = CORRECT_USER,
    category = CORRECT_CATEGORY,
    photos = [photo_obj],
    status_history = [],
    followers = [],
    messages = []
)

@pytest.mark.parametrize(
    "reporter, category_id, title, description, latitude, longitude, photos, is_anonymous",
    [
        (CORRECT_USER, 1, "Titolo valido", "Descrizione valida", 45.0, 9.0, ["foto1.jpg"], False),
    ]
)
def test_create_report_success(reporter, category_id, title, description, latitude, longitude, photos, is_anonymous):
    report_service = ReportService()
    
    # Esecuzione
    result = report_service.create_report(
        reporter=reporter,
        category_id=category_id,
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        photos=photos,
        is_anonymous=is_anonymous
    )
    
    # Verifica
    assert isinstance(result, Report)
    assert result.title == CORRECT_REPORT.title
    assert result.reporter == CORRECT_REPORT.reporter
    assert result.category == CORRECT_REPORT.category
    assert result.description == CORRECT_REPORT.description
    assert result.latitude == CORRECT_REPORT.latitude
    assert result.longitude == CORRECT_REPORT.longitude
    assert result.photos == CORRECT_REPORT.photos
    assert result.is_anonymous == CORRECT_REPORT.is_anonymous

    


@pytest.mark.parametrize(
    "reporter, category_id, title, description, latitude, longitude, photos, is_anonymous",
    [
        (CORRECT_USER, None, "Titolo valido", "Descrizione valida", 45.0, 9.0, ["foto1.jpg"], False),
        
        (CORRECT_USER, -1,"Titolo valido", "Descrizione valida", 45.0, 9.0, ["foto1.jpg"], False),
        
        (CORRECT_USER, 2, "Titolo valido", "Descrizione valida", 45.0, 9.0, ["foto1.jpg"], False),
        
        (CORRECT_USER, 3, "Titolo valido", "Descrizione valida", 45.0, 9.0, ["foto1.jpg"], False),
                
        (CORRECT_USER, 1, "", "Descrizione valida", 45.0, 9.0, ["foto1.jpg"], False),
        
        (CORRECT_USER, 1, "Titolo valido", "", 45.0, 9.0, ["foto1.jpg"], False),
           
        (CORRECT_USER, 1, "Titolo valido", "Descrizione valida", "", 9.0, ["foto1.jpg"], False),
        
        (CORRECT_USER, 1, "Titolo valido", "Descrizione valida", 45.0, "", ["foto1.jpg"], False),
        
        (CORRECT_USER, 1, "Titolo valido", "Descrizione valida", "lat", 9.0, ["foto1.jpg"], False),
        
        (CORRECT_USER, 1, "Titolo valido", "Descrizione valida", 45.0, "long", ["foto1.jpg"], False),
        
        (CORRECT_USER, 1, "Titolo valido", "Descrizione valida", 45.0, 9.0, [], False),
        
        (CORRECT_USER, 1, "Titolo valido", "Descrizione valida", 45.0, 9.0, ["foto1.jpg", "foto2.jpg", "foto3.jpg", "foto4.jpg"], False),
    ]
)
def test_create_report_raises_validation_error(reporter, category_id, title, description, latitude, longitude, photos, is_anonymous):
    report_service = ReportService()
    
    with pytest.raises(ValidationError):
        report_service.create_report(
            reporter=reporter,
            category_id=category_id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            photos=photos,
            is_anonymous=is_anonymous
        )