from course_auto_select.backends.core import Backends


def test_relogin() -> None:
    backend = Backends()
    backend.load_user_info_from_file()
    backend.login()
    assert backend.is_logged_in, "Initial login failed"
    assert backend.validate_session(), "Session validation failed after login"

    # Simulate session expiration
    backend.session.cookies.clear()

    # Attempt to access a protected resource to trigger relogin
    if not backend.validate_session():
        backend.logger.info("Session expired, attempting to relogin...")
        backend.load_user_info_from_file()
        backend.login()
        assert backend.validate_session(), "Session validation failed after relogin"

    assert backend.is_logged_in, "Relogin failed after session expiration"


if __name__ == "__main__":
    test_relogin()
