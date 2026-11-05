from app.services.player_service import (
    generate_display_name,
    hash_session_token,
)


def test_generate_display_name():
    name = generate_display_name()

    assert isinstance(name, str)
    assert len(name) <= 32
    assert name[-4:].isdigit()


def test_hash_session_token():
    token = "some-secret-token"

    hashed = hash_session_token(token)

    assert len(hashed) == 64
    assert hashed != token
    assert hashed == hash_session_token(token)
