"""
Integration tests for error scenarios and edge cases.
Uses AAA (Arrange-Act-Assert) pattern for clarity.
Tests error handling, state consistency, and boundary conditions.
"""

import pytest


class TestErrorScenarios:
    """Integration tests for error handling and edge cases."""

    def test_invalid_email_in_signup_query_param(self, client):
        """
        Test workflow: Invalid email format is sent in query parameter.
        Verifies current behavior - app accepts any string as email.
        """
        # Arrange
        activity_name = "Chess Club"
        invalid_email = "not-an-email"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={invalid_email}"
        )

        # Assert - app currently accepts any string
        # Note: This documents current behavior. Consider adding email validation.
        assert response.status_code == 200

    def test_empty_email_signup(self, client):
        """Test signup with empty email string."""
        # Arrange
        activity_name = "Soccer Team"
        email = ""

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - app currently accepts empty string
        assert response.status_code == 200

    def test_special_characters_in_email(self, client):
        """Test signup with special characters in email."""
        # Arrange
        activity_name = "Drama Club"
        email = "user_tag@domain.co.uk"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - app should handle special characters
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_activity_name_with_special_characters(self, client):
        """Test signup to activity with special characters in name."""
        # Arrange
        # Activity names in the system are fixed, but test with URL encoding

        # Act - Chess Club signup (already exists)
        response = client.post(
            f"/activities/Chess%20Club/signup?email=student@example.com"
        )

        # Assert
        assert response.status_code == 200

    def test_duplicate_signup_state_consistency(self, client):
        """
        Test that after a failed duplicate signup attempt, state is consistent.
        Verifies that failed request doesn't leave data in invalid state.
        """
        # Arrange
        activity_name = "Painting Workshop"
        email = "artist@example.com"

        # Act - first signup
        client.post(f"/activities/{activity_name}/signup?email={email}")
        activities_after_first = client.get("/activities").json()
        count_after_first = len(
            activities_after_first[activity_name]["participants"]
        )

        # Second signup (duplicate) - should fail
        response_duplicate = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert - state unchanged after failed request
        assert response_duplicate.status_code == 400
        activities_after_second = client.get("/activities").json()
        count_after_second = len(
            activities_after_second[activity_name]["participants"]
        )
        assert count_after_first == count_after_second
        assert (
            activities_after_first[activity_name]["participants"]
            == activities_after_second[activity_name]["participants"]
        )

    def test_unregister_from_activity_preserves_other_activities(self, client):
        """
        Test that error/operations in one activity don't affect others.
        Verifies state isolation between activities.
        """
        # Arrange
        email = "student@example.com"
        activity1 = "Science Olympiad"
        activity2 = "Debate Team"

        # Act - signup for both
        client.post(f"/activities/{activity1}/signup?email={email}")
        client.post(f"/activities/{activity2}/signup?email={email}")

        # Attempt to unregister from non-existent activity (error)
        error_response = client.delete(
            f"/activities/Nonexistent/unregister?email={email}"
        )

        # Assert - error occurred
        assert error_response.status_code == 404

        # Assert - other activities unchanged
        activities = client.get("/activities").json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]

    def test_signup_after_failed_unregister(self, client):
        """
        Test that signup succeeds after a failed unregister attempt.
        Verifies that errors don't prevent future operations.
        """
        # Arrange
        activity_name = "Basketball Club"
        email = "player@example.com"

        # Act - signup
        signup = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Unregister non-existent participant (error)
        error_unregister = client.delete(
            f"/activities/{activity_name}/unregister?email=notexist@example.com"
        )

        # Attempt to unregister actual participant
        valid_unregister = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert - signup worked, error didn't prevent valid unregister
        assert signup.status_code == 200
        assert error_unregister.status_code == 404
        assert valid_unregister.status_code == 200

    def test_repeated_failed_operations(self, client):
        """
        Test that repeated failed operations don't corrupt state.
        Verifies system stability under repeated errors.
        """
        # Arrange
        activity_name = "Gym Class"

        # Act - attempt multiple failed operations
        for i in range(5):
            response = client.delete(
                f"/activities/{activity_name}/unregister?email=nonexistent{i}@example.com"
            )
            assert response.status_code == 404

        # Assert - activities list still valid
        activities = client.get("/activities").json()
        assert "Gym Class" in activities
        assert "participants" in activities["Gym Class"]
        assert isinstance(activities["Gym Class"]["participants"], list)

    def test_case_sensitivity_in_email(self, client):
        """
        Test whether email comparison is case-sensitive.
        Documents current behavior.
        """
        # Arrange
        activity_name = "Programming Class"
        email_lower = "student@example.com"
        email_upper = "STUDENT@example.com"

        # Act - signup with lowercase
        client.post(f"/activities/{activity_name}/signup?email={email_lower}")

        # Act - attempt signup with uppercase
        response = client.post(
            f"/activities/{activity_name}/signup?email={email_upper}"
        )

        # Assert - documents current case-sensitive behavior
        # (API treats them as different emails)
        assert response.status_code == 200
        participants = client.get("/activities").json()[activity_name]["participants"]
        assert email_lower in participants
        assert email_upper in participants

    def test_state_after_get_activities_call(self, client):
        """
        Test that calling GET /activities doesn't modify state.
        Verifies that read operations are truly read-only.
        """
        # Arrange
        activities_before = client.get("/activities").json()

        # Act - call GET multiple times
        for _ in range(3):
            activities_mid = client.get("/activities").json()

        activities_after = client.get("/activities").json()

        # Assert - state unchanged
        assert activities_before == activities_mid
        assert activities_before == activities_after

    def test_max_participants_field_present(self, client):
        """
        Test that max_participants field is present but not enforced.
        Documents current behavior - capacity limits are not enforced.
        """
        # Arrange
        activity_name = "Soccer Team"
        max_participants = client.get("/activities").json()[activity_name][
            "max_participants"
        ]

        # Act - signup multiple students beyond capacity
        emails = [f"player{i}@example.com" for i in range(max_participants + 5)]
        signup_responses = [
            client.post(f"/activities/{activity_name}/signup?email={email}")
            for email in emails
        ]

        # Assert - all signups succeed (capacity not enforced)
        for response in signup_responses:
            assert response.status_code == 200

        participants = client.get("/activities").json()[activity_name]["participants"]
        # Note: Current implementation doesn't enforce max_participants
        assert len(participants) > max_participants
