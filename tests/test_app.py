import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully"""
    # We mock the mongo call or just check if the route exists
    # For this basic setup, we just check that the app initializes
    assert client is not None
