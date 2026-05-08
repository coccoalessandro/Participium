from __future__ import annotations

from unittest.mock import Mock
import pytest

from participium.services.user_service import UserService
from participium.models.user import User
from participium.core.exceptions import ValidationError

# --- HELPER: Crea un finto utente "sicuro" ---
def _mock_user(user_id=102, username="luca.bianchi"):
    """Crea un Mock che si comporta come un oggetto User senza attivare SQLAlchemy."""
    user = Mock(spec=User)
    user.id = user_id
    user.username = username
    user.first_name = "Luca"
    user.last_name = "Bianchi"
    user.email_notifications_enabled = True
    user.profile_picture_path = None
    return user

# --- FIXTURE: Prepara il servizio e i suoi componenti ---
@pytest.fixture
def user_service_bundle() -> dict[str, object]:
    session = Mock()
    user_repository = Mock()
    storage_service = Mock()
    
    service = UserService(
        session=session,
        user_repository=user_repository,
        storage_service=storage_service
    )
    
    return {
        "service": service,
        "session": session,
        "user_repository": user_repository,
        "storage_service": storage_service
    }

# --- TEST CASES ---

# TC-1: Aggiornamento con successo (cambio username)
def test_update_profile_success(user_service_bundle: dict[str, object]) -> None:
    service = user_service_bundle["service"]
    repo = user_service_bundle["user_repository"]
    session = user_service_bundle["session"]
    
    current_user = _mock_user()
    new_username = "bianchi.luca"
    
    # Mock: Il database non trova altri utenti con quel nome
    repo.get_by_username.return_value = None

    result = service.update_profile(
        user=current_user, 
        username=new_username, 
        first_name="Gianluca"
    )
    
    assert result.username == new_username
    assert result.first_name == "Gianluca"
    repo.get_by_username.assert_called_with(new_username)
    session.commit.assert_called_once()


# TC-2: Nessun cambiamento (lo username è lo stesso)
def test_update_profile_unchanged(user_service_bundle: dict[str, object]) -> None:
    service = user_service_bundle["service"]
    repo = user_service_bundle["user_repository"]
    
    current_user = _mock_user(username="luca.bianchi")
    
    # Passiamo lo stesso username attuale
    result = service.update_profile(user=current_user, username="luca.bianchi")
    
    assert result.username == "luca.bianchi"
    # Se lo username è uguale, il servizio NON deve interrogare il DB (ottimizzazione)
    repo.get_by_username.assert_not_called()


# TC-3: Fallimento (username già occupato da qualcun altro)
def test_update_profile_unsuccess_already_used(user_service_bundle: dict[str, object]) -> None:
    service = user_service_bundle["service"]
    repo = user_service_bundle["user_repository"]
    
    current_user = _mock_user(user_id=102)
    used_username = "anna.gialli"
    
    # Mock: Il database restituisce un ALTRO utente (id 103) che usa quel nome
    repo.get_by_username.return_value = _mock_user(user_id=103, username="anna.gialli")
    
    with pytest.raises(ValidationError, match="Username already in use"):
        service.update_profile(current_user, username=used_username)


# TC-4: Caricamento immagine del profilo
def test_update_profile_with_picture(user_service_bundle: dict[str, object]) -> None:
    service = user_service_bundle["service"]
    storage = user_service_bundle["storage_service"]
    
    current_user = _mock_user()
    mock_file = Mock() # Simula un file immagine (FileStorage)
    storage.save.return_value = "/static/uploads/profile_102.jpg"
    
    result = service.update_profile(current_user, profile_picture=mock_file)
    
    # Verifica che il percorso sia stato salvato nell'utente
    assert result.profile_picture_path == "/static/uploads/profile_102.jpg"
    storage.save.assert_called_once_with(mock_file)