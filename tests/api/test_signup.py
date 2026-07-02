"""
Tests for the POST /activities/{activity_name}/signup endpoint.
Uses AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest


class TestSignupForActivity:
    """Tests for signing up a student for an activity."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        # Arrange
        activity_name = "Soccer Team"
        email = "new.student@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in client.get("/activities").json()[activity_name]["participants"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that a student is added to the activity's participants list."""
        # Arrange
        activity_name = "Basketball Club"
        email = "basketball.fan@example.com"
        activities_before = client.get("/activities").json()
        participants_before = activities_before[activity_name]["participants"].copy()

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        activities_after = client.get("/activities").json()
        participants_after = activities_after[activity_name]["participants"]
        assert len(participants_after) == len(participants_before) + 1
        assert email in participants_after

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signup to a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice for the same activity returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "chess.player@example.com"

        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act - attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple students can sign up for the same activity."""
        # Arrange
        activity_name = "Drama Club"
        email1 = "actor1@example.com"
        email2 = "actor2@example.com"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email1}"
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email2}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        participants = client.get("/activities").json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants
        assert len(participants) == 2

    def test_signup_preserves_existing_participants(self, client):
        """Test that signing up doesn't remove existing participants."""
        # Arrange
        activity_name = "Gym Class"
        existing_participants = client.get("/activities").json()[activity_name][
            "participants"
        ].copy()
        new_email = "new.athlete@example.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

        # Assert
        assert response.status_code == 200
        participants_after = client.get("/activities").json()[activity_name][
            "participants"
        ]
        for existing in existing_participants:
            assert existing in participants_after
        assert new_email in participants_after

    def test_signup_different_activities(self, client):
        """Test that a student can sign up for multiple different activities."""
        # Arrange
        email = "multi.tasker@example.com"
        activity1 = "Science Olympiad"
        activity2 = "Debate Team"

        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]

    def test_signup_response_structure(self, client):
        """Test that the signup response has the correct structure."""
        # Arrange
        activity_name = "Painting Workshop"
        email = "artist@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
        assert email in data["message"]
        assert activity_name in data["message"]
