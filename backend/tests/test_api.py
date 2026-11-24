"""
Backend API and DockerService unit/integration tests for AgentNest.
"""

import os
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

# Use in-memory SQLite before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test_agentnest.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"

from app.database import Base, engine, SessionLocal
from app.main import app
from app.services.docker_service import DockerService


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _signup_and_login(client: TestClient, email: str, username: str, password: str = "securepass123", full_name: str = "Test User") -> dict:
    resp = client.post(
        "/api/auth/signup",
        json={"email": email, "username": username, "password": password, "full_name": full_name},
    )
    assert resp.status_code == 201, resp.text
    login_resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200, login_resp.text
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_and_root(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    root = client.get("/")
    assert root.status_code == 200
    assert "endpoints" in root.json()


def test_auth_signup_login_and_me(client):
    headers = _signup_and_login(client, "alice@example.com", "alice", full_name="Alice Smith")

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    data = me.json()
    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice"
    assert data["full_name"] == "Alice Smith"

    # Duplicate email fails
    dup = client.post(
        "/api/auth/signup",
        json={"email": "alice@example.com", "username": "alice2", "password": "securepass123"},
    )
    assert dup.status_code == 400

    # Short password rejected by schema validation
    weak = client.post(
        "/api/auth/signup",
        json={"email": "bob@example.com", "username": "bob", "password": "123"},
    )
    assert weak.status_code == 422

    # Wrong password fails login
    bad_login = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "wrongpassword"},
    )
    assert bad_login.status_code == 401


def test_agent_lifecycle_and_tenant_isolation(client):
    alice_headers = _signup_and_login(client, "alice@example.com", "alice")
    bob_headers = _signup_and_login(client, "bob@example.com", "bob")

    mock_docker = MagicMock()
    mock_docker.deploy_agent.return_value = {
        "container_id": "abc123def456",
        "container_name": "agent-1-1",
        "status": "running",
    }
    mock_docker.stop_agent.return_value = True
    mock_docker.start_agent.return_value = True
    mock_docker.delete_agent.return_value = True
    mock_docker.get_agent_logs.return_value = "line 1\nline 2"
    mock_docker.get_agent_stats.return_value = {
        "container_id": "abc123def456",
        "status": "running",
        "cpu_percent": 12.5,
        "memory_usage_mb": 128.0,
        "memory_limit_mb": 512.0,
        "memory_percent": 25.0,
        "uptime_seconds": 3600,
    }

    with patch("app.routes.agents.get_docker_service", return_value=mock_docker):
        # Deploy
        create = client.post(
            "/api/agents",
            headers=alice_headers,
            json={
                "name": "Support Bot",
                "description": "Helps users",
                "docker_image": "python:3.11-slim",
                "cpu_limit": 1.0,
                "memory_limit_mb": 512,
            },
        )
        assert create.status_code == 201, create.text
        agent = create.json()
        agent_id = agent["id"]
        assert agent["status"] == "running"
        assert agent["container_id"] == "abc123def456"
        assert agent["last_started"] is not None
        assert agent["last_run"] is not None

        # Tenant isolation: Bob cannot see or delete Alice's agent
        assert client.get(f"/api/agents/{agent_id}", headers=bob_headers).status_code == 404
        assert client.delete(f"/api/agents/{agent_id}", headers=bob_headers).status_code == 404

        # List
        listed = client.get("/api/agents", headers=alice_headers)
        assert listed.status_code == 200
        assert len(listed.json()) == 1

        # Update
        updated = client.put(
            f"/api/agents/{agent_id}",
            headers=alice_headers,
            json={"name": "Support Bot v2", "cpu_limit": 2.0},
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Support Bot v2"
        assert updated.json()["cpu_limit"] == 2.0

        # Logs & stats
        logs = client.get(f"/api/agents/{agent_id}/logs", headers=alice_headers)
        assert logs.status_code == 200
        assert logs.json()["logs"] == ["line 1", "line 2"]

        stats = client.get(f"/api/agents/{agent_id}/stats", headers=alice_headers)
        assert stats.status_code == 200
        assert stats.json()["stats"]["cpu_percent"] == 12.5

        # Stop & start
        stop = client.post(f"/api/agents/{agent_id}/stop", headers=alice_headers)
        assert stop.status_code == 200
        assert client.get(f"/api/agents/{agent_id}", headers=alice_headers).json()["status"] == "stopped"

        start = client.post(f"/api/agents/{agent_id}/start", headers=alice_headers)
        assert start.status_code == 200
        assert client.get(f"/api/agents/{agent_id}", headers=alice_headers).json()["status"] == "running"

        # Delete
        deleted = client.delete(f"/api/agents/{agent_id}", headers=alice_headers)
        assert deleted.status_code == 200
        assert client.get("/api/agents", headers=alice_headers).json() == []


def test_deploy_failure_rolls_back_db_record(client):
    headers = _signup_and_login(client, "rollback@example.com", "rollback")

    mock_docker = MagicMock()
    mock_docker.deploy_agent.side_effect = Exception("Docker daemon unavailable")

    with patch("app.routes.agents.get_docker_service", return_value=mock_docker):
        resp = client.post(
            "/api/agents",
            headers=headers,
            json={
                "name": "Broken Bot",
                "docker_image": "nonexistent:latest",
            },
        )
        assert resp.status_code == 400
        # Ensure no orphaned 'deploying' record was left behind
        listed = client.get("/api/agents", headers=headers)
        assert listed.status_code == 200
        assert listed.json() == []


def test_docker_service_stats_and_uptime_parsing():
    svc = object.__new__(DockerService)
    svc.client = MagicMock()

    mock_container = MagicMock()
    mock_container.short_id = "1234567890ab"
    mock_container.status = "running"
    mock_container.attrs = {
        "State": {"StartedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.123456789Z")}
    }
    mock_container.stats.return_value = {
        "cpu_stats": {
            "cpu_usage": {"total_usage": 200_000_000, "percpu_usage": [100_000_000, 100_000_000]},
            "system_cpu_usage": 2_000_000_000,
            "online_cpus": 2,
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 100_000_000},
            "system_cpu_usage": 1_000_000_000,
        },
        "memory_stats": {
            "usage": 128 * 1024 * 1024,
            "limit": 512 * 1024 * 1024,
        },
    }
    svc.client.containers.get.return_value = mock_container

    stats = svc.get_agent_stats(agent_id=1, user_id=1)
    assert "error" not in stats
    assert stats["cpu_percent"] == 20.0
    assert stats["memory_usage_mb"] == 128.0
    assert stats["memory_limit_mb"] == 512.0
    assert stats["memory_percent"] == 25.0
    assert isinstance(stats["uptime_seconds"], int)
    assert stats["uptime_seconds"] >= 0
