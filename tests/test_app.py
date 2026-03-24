import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all(self, client):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
    
    def test_activities_have_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        email = "test.student@mergington.edu"
        activity = "Chess Club"
        initial_count = len(activities[activity]["participants"])
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count + 1
        
        # Clean up
        activities[activity]["participants"].remove(email)
    
    def test_signup_duplicate_email(self, client):
        """Test that duplicate signups are rejected"""
        activity = "Chess Club"
        email = activities[activity]["participants"][0]  # Use existing participant
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_multiple_participants(self, client):
        """Test multiple participants can sign up for same activity"""
        activity = "Programming Class"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify both were added
        for email in emails:
            assert email in activities[activity]["participants"]
            activities[activity]["participants"].remove(email)


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        activity = "Tennis Club"
        email = "temp.student@mergington.edu"
        
        # First, sign up
        activities[activity]["participants"].append(email)
        initial_count = len(activities[activity]["participants"])
        
        # Then unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1
    
    def test_unregister_not_registered(self, client):
        """Test unregister for student not registered"""
        activity = "Art Studio"
        email = "not.registered@mergington.edu"
        
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client):
        """Test that student can sign up after unregistering"""
        activity = "Drama Club"
        email = "returning.student@mergington.edu"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Clean up
        activities[activity]["participants"].remove(email)
