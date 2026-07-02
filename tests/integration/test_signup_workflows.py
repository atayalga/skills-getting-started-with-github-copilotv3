"""
Integration tests for signup workflows involving multiple endpoints.
Uses AAA (Arrange-Act-Assert) pattern for clarity.
Tests real-world workflows and multi-step scenarios.
"""

import pytest


class TestSignupWorkflows:
    """Integration tests for complete signup workflows."""

    def test_signup_appears_in_activities_list(self, client):
        """
        Test workflow: Signup → verify participant appears in activities list.
        Verifies that a signup is immediately reflected in GET /activities.
        """
        # Arrange
        activity_name = "Soccer Team"
        email = "soccer.player@example.com"
        activities_before = client.get("/activities").json()
        assert email not in activities_before[activity_name]["participants"]

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert signup_response.status_code == 200
        activities_after = client.get("/activities").json()
        assert email in activities_after[activity_name]["participants"]

    def test_signup_duplicate_unregister_workflow(self, client):
        """
        Test workflow: Signup → attempt duplicate → unregister → verify.
        Verifies that duplicate prevention works and unregister removes the participant.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "chess.master@example.com"

        # Act
        # First signup - should succeed
        signup1 = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Duplicate signup - should fail
        signup2 = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Unregister - should succeed
        unregister = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert signup1.status_code == 200
        assert signup2.status_code == 400
        assert unregister.status_code == 200
        activities_final = client.get("/activities").json()
        assert email not in activities_final[activity_name]["participants"]

    def test_multiple_participants_signup_workflow(self, client):
        """
        Test workflow: Multiple students signup → verify all appear → unregister one.
        Verifies that multiple participants can be managed independently.
        """
        # Arrange
        activity_name = "Basketball Club"
        emails = ["player1@example.com", "player2@example.com", "player3@example.com"]

        # Act - signup all students
        signup_responses = [
            client.post(f"/activities/{activity_name}/signup?email={email}")
            for email in emails
        ]

        # Assert - all signups succeeded
        for response in signup_responses:
            assert response.status_code == 200

        # Act - verify all in activities list
        activities = client.get("/activities").json()
        for email in emails:
            assert email in activities[activity_name]["participants"]

        # Act - unregister one student
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={emails[0]}"
        )

        # Assert - verify one removed, others remain
        assert unregister_response.status_code == 200
        activities_after = client.get("/activities").json()
        assert emails[0] not in activities_after[activity_name]["participants"]
        assert emails[1] in activities_after[activity_name]["participants"]
        assert emails[2] in activities_after[activity_name]["participants"]

    def test_signup_multiple_activities_workflow(self, client):
        """
        Test workflow: Student signs up for multiple activities → verify all.
        Verifies that one student can enroll in multiple activities simultaneously.
        """
        # Arrange
        email = "multi.tasker@example.com"
        activities_to_join = ["Drama Club", "Painting Workshop", "Science Olympiad"]

        # Act - signup for multiple activities
        signup_responses = [
            client.post(f"/activities/{activity}/signup?email={email}")
            for activity in activities_to_join
        ]

        # Assert - all signups succeeded
        for response in signup_responses:
            assert response.status_code == 200

        # Assert - verify student appears in all activities
        activities = client.get("/activities").json()
        for activity_name in activities_to_join:
            assert email in activities[activity_name]["participants"]

    def test_unregister_unaffected_activities_workflow(self, client):
        """
        Test workflow: Student signup for multiple activities → unregister from one.
        Verifies that unregistering from one activity doesn't affect others.
        """
        # Arrange
        email = "student@example.com"
        activity1 = "Debate Team"
        activity2 = "Programming Class"

        # Act - signup for both
        client.post(f"/activities/{activity1}/signup?email={email}")
        client.post(f"/activities/{activity2}/signup?email={email}")

        # Assert - both signups succeeded
        activities = client.get("/activities").json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]

        # Act - unregister from first activity only
        unregister_response = client.delete(
            f"/activities/{activity1}/unregister?email={email}"
        )

        # Assert - unregistered from first, still in second
        assert unregister_response.status_code == 200
        activities_after = client.get("/activities").json()
        assert email not in activities_after[activity1]["participants"]
        assert email in activities_after[activity2]["participants"]

    def test_signup_after_initial_rejection_workflow(self, client):
        """
        Test workflow: Signup to non-existent activity fails → signup to existing one succeeds.
        Verifies that failed signup to one activity doesn't affect ability to signup to another.
        """
        # Arrange
        email = "learner@example.com"
        nonexistent_activity = "Nonexistent Activity"
        valid_activity = "Gym Class"

        # Act - attempt signup to non-existent activity
        invalid_signup = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )

        # Assert - invalid signup failed
        assert invalid_signup.status_code == 404

        # Act - signup to valid activity
        valid_signup = client.post(
            f"/activities/{valid_activity}/signup?email={email}"
        )

        # Assert - valid signup succeeded
        assert valid_signup.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[valid_activity]["participants"]

    def test_signup_unregister_ressignup_workflow(self, client):
        """
        Test workflow: Signup → unregister → signup again.
        Verifies that a student can re-enroll after leaving an activity.
        """
        # Arrange
        activity_name = "Gym Class"
        email = "fitness.enthusiast@example.com"

        # Act - first signup
        signup1 = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - first signup succeeded
        assert signup1.status_code == 200
        activities1 = client.get("/activities").json()
        assert email in activities1[activity_name]["participants"]

        # Act - unregister
        unregister = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert - unregister succeeded
        assert unregister.status_code == 200
        activities2 = client.get("/activities").json()
        assert email not in activities2[activity_name]["participants"]

        # Act - signup again
        signup2 = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - second signup succeeded
        assert signup2.status_code == 200
        activities3 = client.get("/activities").json()
        assert email in activities3[activity_name]["participants"]

    def test_concurrent_signup_same_activity_workflow(self, client):
        """
        Test workflow: Multiple students signup rapidly for the same activity.
        Verifies that the activity correctly tracks all new participants.
        """
        # Arrange
        activity_name = "Science Olympiad"
        emails = [
            f"scientist{i}@example.com" for i in range(1, 6)
        ]  # 5 different students

        # Act - signup all students
        responses = [
            client.post(f"/activities/{activity_name}/signup?email={email}")
            for email in emails
        ]

        # Assert - all signups succeeded
        for response in responses:
            assert response.status_code == 200

        # Assert - verify all are in the activity
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        for email in emails:
            assert email in participants
