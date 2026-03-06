"""Live network login tests against school CAS/EAMS endpoints."""

from __future__ import annotations

import configparser
from pathlib import Path

from course_auto_select.backends.core import Backends


def _load_credentials(config_path: str = "./user_info.secret") -> tuple[str, str]:
    cfg_path = Path(config_path)
    if not cfg_path.exists():
        raise AssertionError(f"config file not found: {config_path}")

    parser = configparser.ConfigParser()
    parser.read(config_path, encoding="utf-8")
    if not parser.has_section("user_info"):
        raise AssertionError("missing [user_info] section in config")

    username = parser.get("user_info", "username", fallback="").strip()
    password = parser.get("user_info", "password", fallback="").strip()
    if not username or not password:
        raise AssertionError("username/password is empty in config")
    return username, password


def test_live_login_success() -> None:
    username, password = _load_credentials()
    backend = Backends()
    backend.login_max_retries = 3
    backend.login(username, password)
    assert backend.is_logged_in, f"live login failed, status tail: {backend.status[-5:]}"
    assert backend.validate_session(), "session invalid right after successful login"
    backend.close()


def test_live_login_idempotent_with_existing_authenticated_session() -> None:
    username, password = _load_credentials()
    backend = Backends()
    backend.login_max_retries = 2
    assert backend.login(username, password), "initial login should succeed"
    assert backend.validate_session(), "session should be valid after initial login"

    second_login_result = backend.login()
    assert second_login_result, f"second login should not fail, status tail: {backend.status[-8:]}"
    assert backend.validate_session(), "session should stay valid after second login"
    backend.close()


def test_live_login_failure_with_wrong_password() -> None:
    username, _ = _load_credentials()
    backend = Backends()
    backend.login_max_retries = 1
    backend.login(username, "__definitely_wrong_password__")
    assert not backend.is_logged_in, "wrong password should never produce logged-in state"
    assert not backend.validate_session(), "wrong password should not get valid session"
    raw_has_wrong_password_text = "您提供的用户名或者密码有误" in (
        backend.last_login_response_text or ""
    )
    status_has_wrong_password_text = any(
        "您提供的用户名或者密码有误" in s for s in backend.status
    )
    # 关键校验：该状态文案必须由真实响应文本驱动，不能凭空出现/消失
    assert (
        raw_has_wrong_password_text == status_has_wrong_password_text
    ), (
        "wrong-password status text is not consistent with real login response: "
        f"raw={raw_has_wrong_password_text}, status={status_has_wrong_password_text}, "
        f"http_status={backend.last_login_response_status}, url={backend.last_login_response_url}"
    )
    backend.close()
