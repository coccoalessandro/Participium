from __future__ import annotations

import pytest

from participium.repositories.category_repository import CategoryRepository
from participium.models.category import Category
from participium.repositories.category_repository import CategoryRepository

pytestmark = pytest.mark.integration


def test_add_persists_category_and_get_by_id_retrieves_it(db_session, make_category):
    cat = make_category(name="Waste Management")
    db_session.commit()

    repo = CategoryRepository(db_session)
    result = repo.get_by_id(cat.id)

    assert result is not None
    assert result.name == "Waste Management"
    assert result.is_active is True


def test_get_by_id_returns_none_when_category_does_not_exist(db_session):
    repo = CategoryRepository(db_session)

    assert repo.get_by_id(9999) is None


def test_add_persists_inactive_category(db_session, make_category):
    cat = make_category(name="Old Category", is_active=False)
    db_session.commit()

    repo = CategoryRepository(db_session)
    result = repo.get_by_id(cat.id)

    assert result is not None
    assert result.is_active is False


def test_get_by_name_returns_matching_category(db_session, make_category):
    make_category(name="Roads")
    db_session.commit()

    repo = CategoryRepository(db_session)
    result = repo.get_by_name("Roads")

    assert result is not None
    assert result.name == "Roads"


def test_get_by_name_returns_none_when_name_does_not_match(db_session):
    repo = CategoryRepository(db_session)

    assert repo.get_by_name("nonexistent") is None


def test_list_all_returns_all_categories(db_session, make_category):
    make_category(name="Alpha")
    make_category(name="Beta")
    make_category(name="Gamma", is_active=False)
    db_session.commit()

    repo = CategoryRepository(db_session)
    results = repo.list_all()

    names = {c.name for c in results}
    assert {"Alpha", "Beta", "Gamma"} <= names


def test_list_all_returns_categories_sorted_alphabetically(db_session, make_category):
    make_category(name="Zeta")
    make_category(name="Alpha")
    make_category(name="Mu")
    db_session.commit()

    repo = CategoryRepository(db_session)
    results = repo.list_all()

    names = [c.name for c in results]
    assert names == sorted(names)


def test_list_all_with_active_only_excludes_inactive_categories(db_session, make_category):
    make_category(name="Active A", is_active=True)
    make_category(name="Active B", is_active=True)
    make_category(name="Inactive", is_active=False)
    db_session.commit()

    repo = CategoryRepository(db_session)
    results = repo.list_all(active_only=True)

    names = {c.name for c in results}
    assert "Active A" in names
    assert "Active B" in names
    assert "Inactive" not in names


def test_list_all_with_active_only_returns_empty_when_no_active_categories(
    db_session, make_category
):
    make_category(name="Old", is_active=False)
    db_session.commit()

    repo = CategoryRepository(db_session)
    results = repo.list_all(active_only=True)

    assert results == []


def test_add_persists_category_via_repository(db_session):

    repo = CategoryRepository(db_session)
    cat = Category(name="Direct Add", is_active=True)
    returned = repo.add(cat)
    db_session.commit()

    assert returned is cat
    assert cat.id is not None