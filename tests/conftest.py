"""Pytest configuration and fixtures."""

import pytest
import sys
import os
import threading
import time
import requests as http_requests
import socket

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

def is_port_available(host, port):
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False

@pytest.fixture(scope="session")
def flask_app():
    """Create and configure a test Flask app."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    return app

@pytest.fixture(scope="session")
def live_server(flask_app):
    """Start a live server for testing HTTP requests."""
    host = '127.0.0.1'
    port = 5001
    
    # Find an available port
    while not is_port_available(host, port) and port < 5010:
        port += 1
    
    if port >= 5010:
        pytest.fail("No available ports found for test server")
    
    # Start the Flask app in a separate thread
    def run_server():
        flask_app.run(
            host=host, 
            port=port, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    base_url = f'http://{host}:{port}'
    
    for _ in range(20):  # Wait up to 20 seconds
        try:
            response = http_requests.get(f'{base_url}/', timeout=2)
            if response.status_code == 200:
                print(f"Test server started successfully at {base_url}")
                break
        except (http_requests.exceptions.ConnectionError, http_requests.exceptions.Timeout):
            time.sleep(1)
    else:
        pytest.fail(f"Failed to start test server at {base_url} after 20 attempts")
    
    yield base_url
    print(f"Test server at {base_url} shutting down")

@pytest.fixture
def api_base_url(live_server):
    """Base URL for API endpoints."""
    return live_server