"""
Pytest configuration and fixtures for the FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_activity():
    """Provide sample activity data for testing."""
    return {
        "description": "Test activity for unit testing",
        "schedule": "Test schedule",
        "max_participants": 5,
        "participants": ["test1@mergington.edu", "test2@mergington.edu"]
    }


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    from src.app import activities
    
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset to known state before test
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)