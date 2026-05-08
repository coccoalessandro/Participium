from __future__ import annotations

from unittest.mock import Mock, patch
import pytest
from pathlib import Path

from participium.services.email_service import BaseEmailGateway, ConsoleEmailGateway, SmtpEmailGateway, build_email_gateway;

# TC-1
def test_base_email_gateway_send(capsys) -> None:
    gateway = BaseEmailGateway()
    gateway.send("test@test.com", "Subject", "Body")
    
    captured = capsys.readouterr()
    assert "Simulating email send operation." in captured.out
    
# TC-2
def test_console_email_gateway_send(tmp_path: Path) -> None:
    gateway = ConsoleEmailGateway(outbox_dir=tmp_path, sender="admin@example.com")
    
    gateway.send("user@example.com", "Benvenuto", "Ciao User!")
    
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    
    content = files[0].read_text(encoding="utf-8")
    assert "FROM: admin@example.com" in content
    assert "TO: user@example.com" in content
    assert "SUBJECT: Benvenuto" in content
    assert "Ciao User!" in content

# TC-3
@patch("smtplib.SMTP")
def test_smtp_gateway_send_full(mock_smtp_class) -> None:
    gateway = SmtpEmailGateway(
        host="smtp.gmail.com", port=587, 
        username="user", password="pwd", 
        sender="admin@example.com", use_tls=True
    )
    
    gateway.send("user@example.com", "Test TLS", "Body TLS")
    
    mock_smtp_instance = mock_smtp_class.return_value.__enter__.return_value
    
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("user", "pwd")
    mock_smtp_instance.send_message.assert_called_once()

# TC-4
@patch("smtplib.SMTP")
def test_smtp_gateway_send_basic(mock_smtp_class) -> None:
    gateway = SmtpEmailGateway(
        host="localhost", port=25, 
        username=None, password=None, 
        sender="admin@example.com", use_tls=False
    )
    
    gateway.send("user@example.com", "Test Basic", "Body Basic")
    
    mock_smtp_instance = mock_smtp_class.return_value.__enter__.return_value
    
    mock_smtp_instance.starttls.assert_not_called()
    mock_smtp_instance.login.assert_not_called()
    mock_smtp_instance.send_message.assert_called_once()

# TC-5
def test_build_email_gateway_returns_smtp() -> None:
    settings = Mock()
    settings.mail_backend = "smtp"
    settings.smtp_host = "smtp.test.com"
    settings.smtp_port = 587
    settings.smtp_username = "user"
    settings.smtp_password = "pwd"
    settings.mail_from = "admin@test.com"
    settings.smtp_use_tls = True

    gateway = build_email_gateway(settings)
    
    assert isinstance(gateway, SmtpEmailGateway)
    assert gateway.host == "smtp.test.com"
    assert gateway.use_tls is True

#TC-6
def test_build_email_gateway_returns_console(tmp_path: Path) -> None:
    settings = Mock()
    settings.mail_backend = "console"
    settings.smtp_host = None 
    settings.mail_outbox_dir = tmp_path
    settings.mail_from = "admin@test.com"

    gateway = build_email_gateway(settings)
    
    assert isinstance(gateway, ConsoleEmailGateway)
    assert gateway.outbox_dir == tmp_path