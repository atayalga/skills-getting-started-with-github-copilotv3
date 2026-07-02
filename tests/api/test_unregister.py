"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint.
Uses AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest


class TestUnregisterFromActivity:
    """Tests for unregistering a student from an activity."""

    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity."""
        # Arrange
        activity_name = "Soccer Team"
        email = "player@example.com"
        # First, sign up the student
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert (
            response.json()["message"]
            == f"Unregistered {email} from {activity_name}"
        )
        assert email not in client.get("/activities").json()[activity_name][
            "participants"
        ]

    def test_unregister_removes_participant(self, client):
        """Test that unregistering removes the student from the activity."""
        # Arrange
        activity_name = "Basketball Club"
        email = "basketball.player@example.com"
        client.post(f"/activities/{activity_name}/signup?email={email}")
        participants_before = len(
            client.get("/activities").json()[activity_name]["participants"]
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        participants_after = len(
            client.get("/activities").json()[activity_name]["participants"]
        )
        assert participants_after == participants_before - 1

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that unregistering a non-existent participant returns 404."""
        # Arrange
        activity_name = "Drama Club"
        email = "not.enrolled@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not found in this activity"

    def test_unregister_preserves_other_participants(self, client):
        """Test that unregistering one student doesn't remove others."""
        # Arrange
        activity_name = "Chess Club"
        existing_participants = client.get("/activities").json()[activity_name][
            "participants"
        ].copy()
        new_email = "chess.novice@example.com"
        client.post(f"/activities/{activity_name}/signup?email={new_email}")

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        participants_after = client.get("/activities").json()[activity_name][
            "participants"
        ]
        for existing in existing_participants:
            assert existing in participants_after

    def test_unregister_response_structure(self, client):
        """Test that the unregister response has the correct structure."""
        # Arrange
        activity_name = "Painting Workshop"
        email = "painter@example.com"
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_twice_returns_404(self, client):
        """Test that unregistering twice returns 404 on the second attempt."""
        # Arrange
        activity_name = "Science Olympiad"
        email = "scientist@example.com"
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # First unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Act - attempt to unregister again
        response2 = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 404
        assert "not found" in response2.json()["detail"]

    def test_signup_after_unregister_succeeds(self, client):
        """Test that a student can re-signup after unregistering."""
        # Arrange
        activity_name = "Debate Team"
        email = "debater@example.com"

        # Act - sign up
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        # Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        # Sign up again
        response3 = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        assert email in client.get("/activities").json()[activity_name]["participants"]
