"""healthz 契约测试。"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_returns_ok_and_protocol_version() -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["protocol_version"] == 1


def test_healthz_does_not_leak_sensitive_fields() -> None:
    """健康检查不得暴露路径、模型或密钥信息。"""
    body = client.get("/healthz").json()
    forbidden = {"path", "model", "models", "key", "token", "secret", "cwd"}
    assert not (forbidden & body.keys())
