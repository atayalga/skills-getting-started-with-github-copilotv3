"""
Tests for the GET /activities endpoint.
Uses AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest


class TestGetActivities:
    """Tests for retrieving all activities."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status code 200."""
        # Arrange
        # (no setup needed, using fixture)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned in the response."""
        # Arrange
        expected_activity_names = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Basketball Club",
            "Drama Club",
            "Painting Workshop",
            "Science Olympiad",
            "Debate Team",
        }

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert set(activities.keys()) == expected_activity_names

    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has the required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_details in activities.items():
            assert set(activity_details.keys()) == required_fields
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            assert isinstance(activity_details["max_participants"], int)
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_participants_are_strings(self, client):
        """Test that all participants are email strings."""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_details in activities.items():
            for participant in activity_details["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation

    def test_get_activities_returns_participants_in_order(self, client):
        """Test that existing participants are returned in the activity."""
        # Arrange
        # Activities are initialized with some participants

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        # Chess Club should have the initial participants
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]

        # Programming Class should have initial participants
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]
