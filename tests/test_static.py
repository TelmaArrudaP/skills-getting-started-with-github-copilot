"""
Test cases for static file serving and frontend functionality.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestStaticFiles:
    """Test cases for static file serving."""
    
    def test_static_index_html_accessible(self, client):
        """Test that static index.html is accessible."""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_static_css_accessible(self, client):
        """Test that static CSS file is accessible."""
        response = client.get("/static/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
    
    def test_static_js_accessible(self, client):
        """Test that static JavaScript file is accessible."""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        # JavaScript might be served as application/javascript or text/javascript
        content_type = response.headers.get("content-type", "")
        assert any(js_type in content_type for js_type in ["javascript", "text/plain"])
    
    def test_root_redirects_to_static(self, client):
        """Test that root URL redirects to static content."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [200, 302, 307]  # Various redirect status codes
    
    def test_nonexistent_static_file(self, client):
        """Test accessing a non-existent static file."""
        response = client.get("/static/nonexistent.txt")
        assert response.status_code == 404


class TestHTMLContent:
    """Test HTML content validation."""
    
    def test_index_html_contains_required_elements(self, client):
        """Test that index.html contains the required form elements."""
        response = client.get("/static/index.html")
        content = response.text
        
        # Check for essential form elements
        assert 'id="signup-form"' in content
        assert 'id="email"' in content
        assert 'id="activity"' in content
        assert 'id="activities-list"' in content
        
        # Check for CSS and JS includes
        assert 'href="styles.css"' in content
        assert 'src="app.js"' in content
    
    def test_css_contains_activity_styles(self, client):
        """Test that CSS contains styles for activity elements."""
        response = client.get("/static/styles.css")
        content = response.text
        
        # Check for activity-related CSS classes
        assert ".activity-card" in content
        assert ".participants-list" in content
        assert ".delete-participant" in content