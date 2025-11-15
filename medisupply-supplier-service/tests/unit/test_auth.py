import pytest


def test_verify_token_with_user_service_success(monkeypatch):
    # monkeypatch requests.get to simulate user-service returning 200
    class FakeResp:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data

        def json(self):
            return self._json

    def fake_get(url, headers, timeout):
        return FakeResp(200, {"id": 1, "email": "u@test"})

    monkeypatch.setattr('app.core.auth.requests.get', fake_get)
    from app.core.auth import verify_token_with_user_service

    res = verify_token_with_user_service('token123')
    assert isinstance(res, dict)
    assert res['email'] == 'u@test'


def test_verify_token_with_user_service_failure(monkeypatch):
    # Simulate requests raising an exception or non-200
    import requests

    def fake_get_err(url, headers, timeout):
        raise requests.RequestException("network")

    monkeypatch.setattr('app.core.auth.requests.get', fake_get_err)
    from app.core.auth import verify_token_with_user_service

    assert verify_token_with_user_service('token123') is None
