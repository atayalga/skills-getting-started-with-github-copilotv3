"""
Pytest configuration and shared fixtures for all tests.
"""

import copy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Deep copy activities for each test to ensure test isolation.
    Prevents tests from modifying shared state.
    """
    original_activities = copy.deepcopy(app_module.activities)
    
    yield
    
    # Restore original activities after test
    app_module.activities.clear()
    app_module.activities.update(original_activities)


@pytest.fixture
def client():
    """
    Provide a TestClient instance for making API requests in tests.
    """
    return TestClient(app_module.app)
