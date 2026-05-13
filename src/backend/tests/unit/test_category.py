from __future__ import annotations

from unittest.mock import Mock, patch
import pytest

from participium.services.category_service import CategoryService
from participium.models.category import Category
from participium.core.exceptions import ValidationError, NotFoundError

CORRECT_CATEGORY = Category(
    id=1, name="New", is_active= True
)

@pytest.fixture
def category_service_bundle() -> dict[str, object]:
    session = Mock()
    category_repository = Mock()
    
    service = CategoryService(
        session=session,
        category_repository=category_repository,
    )
    
    return {
        "service": service,
        "category_repository": category_repository,
    }


#TC-1 
def test_get_category_success(category_service_bundle: dict[str, object]) -> None: 
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
    
    mock_category = Mock(spec=Category)
    mock_category.id = 1
    category_repository.get_by_id.return_value = mock_category

    result_category = service.get_category(mock_category.id)

    assert isinstance(result_category, Category)
    assert result_category.id == mock_category.id

# TC-2
def test_get_category_not_found(category_service_bundle: dict[str, object]) -> None:
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
   
    mock_category = Mock(spec=Category)
    mock_category.id = 99
    category_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_category(mock_category.id)


# TC-3
def test_list_categories_success(category_service_bundle: dict[str, object]) -> None:
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
    
    mock_category1 = Mock(spec=Category)
    mock_category1.id = 1
    mock_category2 = Mock(spec=Category)
    mock_category2.id = 2
    category_repository.list_all.return_value = [mock_category1, mock_category2]

    result_categories = service.list_categories()

    assert isinstance(result_categories, list)
    assert len(result_categories) == 2
    assert all(isinstance(cat, Category) for cat in result_categories)


# TC-4
def test_create_category_success(category_service_bundle: dict[str, object]) -> None:
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
    """
    mock_category = Mock()
    mock_category.name = "New"
    """
    category_repository.get_by_name.return_value = None
    category_repository.add.return_value = CORRECT_CATEGORY
    result_category = service.create_category(CORRECT_CATEGORY.name)

    assert isinstance(result_category, Category)
    assert result_category.name == CORRECT_CATEGORY.name

# TC-5
def test_create_category_already_used_unsuccess(category_service_bundle: dict[str, object]) -> None:
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
    
    mock_category = Mock(spec=Category)
    mock_category.name = "Waste"
    category_repository.get_by_name.return_value = mock_category

    with pytest.raises(ValidationError):
        service.create_category(mock_category.name)

# TC-6
def test_create_category_not_string_unsuccess(category_service_bundle: dict[str, object]) -> None:
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
    
    mock_category = Mock(spec=Category)
    mock_category.name = "   "

    with pytest.raises(ValidationError):
        service.create_category(mock_category.name)


# TC-7
def test_update_category_success(category_service_bundle: dict[str, object]) -> None:
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
    
    mock_category = Mock(spec=Category)
    mock_category.id = 1
    mock_category.name = "New"
    category_repository.get_by_id.return_value = mock_category
    category_repository.get_by_name.return_value = None

    result_category = service.update_category(mock_category.id, name=mock_category.name)

    assert isinstance(result_category, Category)
    assert result_category.id == mock_category.id
    assert result_category.name == mock_category.name

# TC-8
def test_update_category_already_used_name_unsuccess(category_service_bundle: dict[str, object]) -> None:
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
    
    mock_category = Mock(spec=Category)
    mock_category.id = 1
    mock_category.name = "Waste"
    category_repository.get_by_name.return_value = mock_category

    with pytest.raises(ValidationError):
        service.update_category(mock_category.id, name=mock_category.name)

# TC-9
def test_update_category_skip_name_success(category_service_bundle: dict[str, object]) -> None:
    service = category_service_bundle["service"]
    category_repository = category_service_bundle["category_repository"]
    
    mock_category = Mock(spec=Category)
    mock_category.id = 1
    mock_category.is_active = True
    category_repository.get_by_id.return_value = mock_category
    category_repository.get_by_name.return_value = None

    result_category = service.update_category(mock_category.id, is_active = mock_category.is_active)

    assert isinstance(result_category, Category)
    assert result_category.id == mock_category.id
    assert result_category.is_active == mock_category.is_active
