from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from participium.services.storage_service import StorageService, LocalFileStorageService

pytestmark = pytest.mark.whitebox

def _make_file_storage(*, filename: str = "photo.jpg") -> Mock:
    """Return a Mock that mimics werkzeug.datastructures.FileStorage."""
    mock_file = Mock()
    mock_file.filename = filename
    return mock_file


@pytest.fixture
def base_storage_service() -> StorageService:
    return StorageService()


@pytest.fixture
def local_storage_bundle(tmp_path: Path) -> dict[str, object]:
    media_root = tmp_path / "media"
    service = LocalFileStorageService(media_root=media_root)
    return {
        "service": service,
        "media_root": media_root,
    }


@pytest.fixture
def local_storage_with_file(local_storage_bundle: dict[str, object]) -> dict[str, object]:
    uploaded_file = _make_file_storage(filename="report.png")
    local_storage_bundle["uploaded_file"] = uploaded_file
    return local_storage_bundle


@pytest.fixture
def local_storage_with_no_filename(local_storage_bundle: dict[str, object]) -> dict[str, object]:
    uploaded_file = _make_file_storage(filename="")
    uploaded_file.filename = None          
    local_storage_bundle["uploaded_file"] = uploaded_file
    return local_storage_bundle


def test_base_storage_service_save_returns_simulated_file(
    base_storage_service: StorageService,
) -> None:
    uploaded_file = _make_file_storage()

    result = base_storage_service.save(uploaded_file)

    assert result == "simulated-file"


def test_base_storage_service_save_does_not_call_file_save(
    base_storage_service: StorageService,
) -> None:
    uploaded_file = _make_file_storage()

    base_storage_service.save(uploaded_file)

    uploaded_file.save.assert_not_called()


def test_local_storage_service_creates_media_root_directory(
    tmp_path: Path,
) -> None:
    media_root = tmp_path / "new_dir" / "nested"

    assert not media_root.exists()

    LocalFileStorageService(media_root=media_root)

    assert media_root.exists()
    assert media_root.is_dir()


def test_local_storage_service_does_not_raise_if_directory_already_exists(
    tmp_path: Path,
) -> None:
    media_root = tmp_path / "already_there"
    media_root.mkdir(parents=True, exist_ok=True)

    # Should not raise
    LocalFileStorageService(media_root=media_root)


def test_local_storage_save_returns_a_string(
    local_storage_with_file: dict[str, object],
) -> None:
    service: LocalFileStorageService = local_storage_with_file["service"]
    uploaded_file = local_storage_with_file["uploaded_file"]

    result = service.save(uploaded_file)

    assert isinstance(result, str)


def test_local_storage_save_calls_file_save_once(
    local_storage_with_file: dict[str, object],
) -> None:
    service: LocalFileStorageService = local_storage_with_file["service"]
    uploaded_file = local_storage_with_file["uploaded_file"]

    service.save(uploaded_file)

    uploaded_file.save.assert_called_once()


def test_local_storage_save_stores_file_inside_media_root(
    local_storage_with_file: dict[str, object],
) -> None:
    service: LocalFileStorageService = local_storage_with_file["service"]
    media_root: Path = local_storage_with_file["media_root"]
    uploaded_file = local_storage_with_file["uploaded_file"]

    service.save(uploaded_file)

    destination: Path = uploaded_file.save.call_args[0][0]
    assert destination.parent == media_root


def test_local_storage_save_relative_name_contains_original_filename(
    local_storage_with_file: dict[str, object],
) -> None:
    service: LocalFileStorageService = local_storage_with_file["service"]
    uploaded_file = local_storage_with_file["uploaded_file"]

    relative_name = service.save(uploaded_file)

    assert relative_name.endswith("report.png")


def test_local_storage_save_relative_name_has_uuid_prefix(
    local_storage_with_file: dict[str, object],
) -> None:
    service: LocalFileStorageService = local_storage_with_file["service"]
    uploaded_file = local_storage_with_file["uploaded_file"]

    relative_name = service.save(uploaded_file)

    parts = relative_name.split("_", 1)
    assert len(parts) == 2
    uuid_part = parts[0]
    assert len(uuid_part) == 32
    assert uuid_part.isalnum()


def test_local_storage_save_two_calls_produce_different_names(
    local_storage_with_file: dict[str, object],
) -> None:
    service: LocalFileStorageService = local_storage_with_file["service"]
    uploaded_file = local_storage_with_file["uploaded_file"]

    name_a = service.save(uploaded_file)
    name_b = service.save(uploaded_file)

    assert name_a != name_b


def test_local_storage_save_falls_back_to_attachment_bin_when_filename_is_none(
    local_storage_with_no_filename: dict[str, object],
) -> None:
    service: LocalFileStorageService = local_storage_with_no_filename["service"]
    uploaded_file = local_storage_with_no_filename["uploaded_file"]

    relative_name = service.save(uploaded_file)

    assert relative_name.endswith("attachment.bin")


def test_local_storage_save_destination_path_matches_returned_name(
    local_storage_with_file: dict[str, object],
) -> None:
    service: LocalFileStorageService = local_storage_with_file["service"]
    media_root: Path = local_storage_with_file["media_root"]
    uploaded_file = local_storage_with_file["uploaded_file"]

    relative_name = service.save(uploaded_file)

    expected_destination = media_root / relative_name
    actual_destination: Path = uploaded_file.save.call_args[0][0]
    assert actual_destination == expected_destination