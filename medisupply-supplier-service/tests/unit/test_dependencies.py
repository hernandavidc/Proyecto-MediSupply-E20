import os


class FakeState:
    pass


class FakeRequest:
    def __init__(self, headers=None, path='/'):
        self.headers = headers or {}
        self.url = type('u', (), {'path': path})
        self.state = FakeState()


def test_get_current_user_auth_disabled(monkeypatch):
    monkeypatch.setenv('AUTH_DISABLED', 'true')
    from app.core.dependencies import get_current_user

    req = FakeRequest()
    user = get_current_user(req, credentials=None)
    assert isinstance(user, dict)
    assert user['email'] == 'test@local'


def test_get_current_user_header_token(monkeypatch):
    # Ensure auth enabled and monkeypatch verify_token_with_user_service
    monkeypatch.setenv('AUTH_DISABLED', 'false')
    def fake_verify(token):
        return {'id': 5, 'email': 'ok@test'}

    monkeypatch.setattr('app.core.dependencies.verify_token_with_user_service', fake_verify)
    from app.core.dependencies import get_current_user

    req = FakeRequest(headers={'authorization': 'Bearer abc123'})
    user = get_current_user(req, credentials=None)
    assert user['email'] == 'ok@test'
