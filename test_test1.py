"""Tests for the Cloudsmith Flask demo application."""

import pytest

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_returns_200(client):
    """Test that the index page returns successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Cloudsmith" in response.data


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_api_info_endpoint(client):
    """Test the API info endpoint."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.get_json()
    assert "hostname" in data
    assert "python_version" in data
    assert "platform" in data


def test_api_stats_endpoint(client):
    """Test the API stats endpoint."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert "request_count" in data
    assert data["version"] == "1.0.0"
    assert "build_number" in data


def test_api_sbom_endpoint(client):
    """Test the SBOM endpoint."""
    response = client.get("/api/sbom")
    assert response.status_code == 200
    data = response.get_json()
    assert data["format"] == "cloudsmith-sbom-lite"
    assert "packages" in data
    assert isinstance(data["packages"], list)
    assert len(data["packages"]) > 0
    assert "name" in data["packages"][0]
    assert "version" in data["packages"][0]
    assert "python_version" in data
    assert "architecture" in data


def test_api_info_includes_build_metadata(client):
    """Test that API info includes build metadata."""
    response = client.get("/api/info")
    data = response.get_json()
    assert "build_number" in data
    assert "build_date" in data
    assert "git_sha" in data


def test_index_contains_pipeline(client):
    """Test that the index page contains the supply chain pipeline."""
    response = client.get("/")
    assert b"Supply Chain Pipeline" in response.data
    assert b"Chainguard" in response.data
    assert b"Cloudsmith Docker" in response.data


def test_index_contains_dependencies(client):
    """Test that the index page shows installed Python dependencies."""
    response = client.get("/")
    assert b"Python Dependencies" in response.data
    assert b"flask" in response.data.lower()
