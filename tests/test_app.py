"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_with_valid_data_returns_200(self):
        """Test signup with valid data returns 200"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self):
        """Test signup returns a success message"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "signed up" in data["message"].lower()

    def test_signup_for_nonexistent_activity_returns_404(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_returns_400(self):
        """Test signing up twice returns 400"""
        email = "duplicate@mergington.edu"
        # First signup
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        # Duplicate signup
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_participant_returns_200(self):
        """Test unregistering a participant returns 200"""
        email = "unregister_test@mergington.edu"
        # First signup
        client.post(f"/activities/Chess Club/signup?email={email}")
        # Then unregister
        response = client.post(
            "/activities/Chess Club/unregister",
            json={"participant": email}
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self):
        """Test unregister returns a success message"""
        email = "unreg@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        response = client.post(
            "/activities/Chess Club/unregister",
            json={"participant": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "unregistered" in data["message"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self):
        """Test unregistering from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            json={"participant": "test@mergington.edu"}
        )
        assert response.status_code == 404

    def test_unregister_nonexistent_participant_returns_400(self):
        """Test unregistering non-existent participant returns 400"""
        response = client.post(
            "/activities/Chess Club/unregister",
            json={"participant": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "remove_test@mergington.edu"
        # Signup
        client.post(f"/activities/Chess Club/signup?email={email}")
        # Verify participant is in list
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        # Unregister
        client.post(
            "/activities/Chess Club/unregister",
            json={"participant": email}
        )
        # Verify participant is removed
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]
