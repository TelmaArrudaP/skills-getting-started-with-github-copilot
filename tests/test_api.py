"""
Test cases for the FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/")
        assert response.status_code == 200
        # The redirect should ultimately serve the static content


class TestActivitiesEndpoint:
    """Test cases for the activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have the expected activities
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in data
            
        # Check structure of each activity
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_structure(self, client):
        """Test the structure of activity data."""
        response = client.get("/activities")
        data = response.json()
        
        # Test Chess Club specifically
        chess_club = data.get("Chess Club")
        assert chess_club is not None
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test cases for the activity signup endpoint."""
    
    def test_signup_for_existing_activity_success(self, client):
        """Test successful signup for an existing activity."""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist."""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signups are prevented."""
        # First signup should succeed
        response1 = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_activity_full(self, client):
        """Test signup when activity is at max capacity."""
        # Fill up the Chess Club (max 12 participants)
        # First, get current participants count
        activities_response = client.get("/activities")
        chess_participants = len(activities_response.json()["Chess Club"]["participants"])
        
        # Add participants until we reach the limit
        for i in range(12 - chess_participants):
            response = client.post(f"/activities/Chess Club/signup?email=student{i}@mergington.edu")
            if response.status_code != 200:
                break
        
        # Now try to add one more - should fail
        response = client.post("/activities/Chess Club/signup?email=overflow@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Activity is full"
    
    def test_signup_url_encoding(self, client):
        """Test signup with URL-encoded activity names."""
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        
        response = client.post(f"/activities/{encoded_name}/signup?email=encoder@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant was added to the correct activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "encoder@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Test cases for the activity unregister endpoint."""
    
    def test_unregister_existing_participant(self, client):
        """Test successful unregistration of an existing participant."""
        # First, sign up a participant
        signup_response = client.post("/activities/Chess Club/signup?email=tobedeleted@mergington.edu")
        assert signup_response.status_code == 200
        
        # Then unregister them
        response = client.delete("/activities/Chess Club/unregister?email=tobedeleted@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered tobedeleted@mergington.edu from Chess Club"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "tobedeleted@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist."""
        response = client.delete("/activities/Nonexistent Activity/unregister?email=test@mergington.edu")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_non_registered_participant(self, client):
        """Test unregistration of a participant who isn't registered."""
        response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_existing_participant_from_default_data(self, client):
        """Test unregistering a participant who was in the default data."""
        # Unregister michael@mergington.edu who should be in Chess Club by default
        response = client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        
        # Verify they were removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple operations."""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test a complete signup and unregister workflow."""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # 1. Initial state - participant should not be registered
        activities_response = client.get("/activities")
        initial_participants = activities_response.json()[activity]["participants"]
        assert email not in initial_participants
        
        # 2. Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # 3. Verify signup
        activities_response = client.get("/activities")
        after_signup_participants = activities_response.json()[activity]["participants"]
        assert email in after_signup_participants
        assert len(after_signup_participants) == len(initial_participants) + 1
        
        # 4. Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # 5. Verify unregistration
        activities_response = client.get("/activities")
        final_participants = activities_response.json()[activity]["participants"]
        assert email not in final_participants
        assert len(final_participants) == len(initial_participants)
    
    def test_multiple_activities_signup(self, client):
        """Test signing up for multiple different activities."""
        email = "multisport@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]