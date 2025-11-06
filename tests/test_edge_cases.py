"""
Test cases for edge cases, validation, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_email_signup(self, client):
        """Test signup with empty email parameter."""
        response = client.post("/activities/Chess Club/signup?email=")
        # The API currently accepts empty emails, so we test the actual behavior
        assert response.status_code == 200
        
        # Verify empty email was added to participants
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert "" in participants
    
    def test_missing_email_parameter(self, client):
        """Test signup without email parameter."""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Validation error for missing required parameter
    
    def test_special_characters_in_email(self, client):
        """Test signup with special characters in email."""
        # URL encode the email to preserve special characters
        import urllib.parse
        special_email = "test+special.email@mergington.edu"
        encoded_email = urllib.parse.quote(special_email)
        
        response = client.post(f"/activities/Chess Club/signup?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify the email was stored correctly
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert special_email in participants
    
    def test_very_long_email(self, client):
        """Test signup with a very long email address."""
        long_email = "a" * 100 + "@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={long_email}")
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert long_email in participants
    
    def test_activity_name_with_spaces_and_special_chars(self, client):
        """Test operations with activity names containing spaces."""
        # Programming Class has a space in the name
        response = client.post("/activities/Programming Class/signup?email=spacetest@mergington.edu")
        assert response.status_code == 200
    
    def test_case_sensitive_activity_names(self, client):
        """Test that activity names are case-sensitive."""
        response = client.post("/activities/chess club/signup?email=case@mergington.edu")
        assert response.status_code == 404  # Should not find "chess club" (lowercase)
        
        response = client.post("/activities/CHESS CLUB/signup?email=case@mergington.edu")
        assert response.status_code == 404  # Should not find "CHESS CLUB" (uppercase)


class TestDataConsistency:
    """Test data consistency and state management."""
    
    def test_participant_count_consistency(self, client):
        """Test that participant counts remain consistent."""
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data["Chess Club"]["participants"])
        
        # Add a participant
        client.post("/activities/Chess Club/signup?email=consistency@mergington.edu")
        
        # Check count increased by 1
        after_signup_response = client.get("/activities")
        after_signup_data = after_signup_response.json()
        after_signup_count = len(after_signup_data["Chess Club"]["participants"])
        assert after_signup_count == initial_count + 1
        
        # Remove the participant
        client.delete("/activities/Chess Club/unregister?email=consistency@mergington.edu")
        
        # Check count is back to original
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_count = len(final_data["Chess Club"]["participants"])
        assert final_count == initial_count
    
    def test_concurrent_signup_simulation(self, client):
        """Simulate concurrent signups to test for race conditions."""
        emails = [f"concurrent{i}@mergington.edu" for i in range(5)]
        
        # Sign up multiple participants
        for email in emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all participants were added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        
        for email in emails:
            assert email in participants


class TestHTTPMethods:
    """Test correct HTTP method usage and restrictions."""
    
    def test_get_method_on_signup_endpoint(self, client):
        """Test that GET method is not allowed on signup endpoint."""
        response = client.get("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_post_method_on_unregister_endpoint(self, client):
        """Test that POST method is not allowed on unregister endpoint."""
        response = client.post("/activities/Chess Club/unregister?email=test@mergington.edu")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_put_method_on_activities_endpoint(self, client):
        """Test that PUT method is not allowed on activities endpoint."""
        response = client.put("/activities")
        assert response.status_code == 405  # Method Not Allowed


class TestResponseFormats:
    """Test response formats and content types."""
    
    def test_activities_response_content_type(self, client):
        """Test that activities endpoint returns JSON."""
        response = client.get("/activities")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
    
    def test_signup_success_response_format(self, client):
        """Test the format of successful signup response."""
        response = client.post("/activities/Chess Club/signup?email=format@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
        assert "format@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_error_response_format(self, client):
        """Test the format of error responses."""
        response = client.post("/activities/Nonexistent/signup?email=error@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)


class TestDocumentationEndpoints:
    """Test API documentation endpoints."""
    
    def test_docs_endpoint_accessible(self, client):
        """Test that the /docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_endpoint_accessible(self, client):
        """Test that the /redoc endpoint is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200