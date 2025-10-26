"""
CORS Testing Script for E-Commerce API

This script simulates HTTP requests from different origins to test CORS configuration.
It verifies that:
1. Allowed origins can access the API
2. Unauthorized origins are blocked
3. Preflight (OPTIONS) requests work correctly
4. Headers are properly configured

Usage:
    python test_cors.py

Requirements:
    pip install requests
"""

import requests
import json
from typing import Dict, Optional

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def test_cors_request(
    api_url: str,
    origin: str,
    method: str = "GET",
    endpoint: str = "/products",
    data: Optional[Dict] = None,
    token: Optional[str] = None
):
    """
    Test a CORS request from a specific origin.

    Args:
        api_url: Base API URL (e.g., http://localhost:8000)
        origin: Origin header to send (e.g., http://localhost:3000)
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint to test
        data: Request body data (for POST/PUT)
        token: JWT token for authenticated requests
    """
    url = f"{api_url}{endpoint}"
    headers = {
        "Origin": origin,
        "Content-Type": "application/json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"\n{Colors.BOLD}Testing: {method} {url}{Colors.RESET}")
    print(f"Origin: {origin}")

    try:
        # First, send OPTIONS request (preflight)
        print(f"\n{Colors.YELLOW}1. Sending OPTIONS (preflight) request...{Colors.RESET}")
        options_response = requests.options(
            url,
            headers=headers,
            timeout=5
        )

        print(f"Status Code: {options_response.status_code}")
        print(f"Response Headers:")
        cors_headers = {
            k: v for k, v in options_response.headers.items()
            if k.lower().startswith('access-control')
        }
        for key, value in cors_headers.items():
            print(f"  {key}: {value}")

        # Check CORS headers
        allow_origin = options_response.headers.get('Access-Control-Allow-Origin')
        allow_methods = options_response.headers.get('Access-Control-Allow-Methods')
        allow_headers = options_response.headers.get('Access-Control-Allow-Headers')
        allow_credentials = options_response.headers.get('Access-Control-Allow-Credentials')

        if allow_origin:
            if allow_origin == origin or allow_origin == "*":
                print_success(f"CORS allowed for origin: {origin}")
            else:
                print_warning(f"Different origin returned: {allow_origin}")
        else:
            print_error("No Access-Control-Allow-Origin header found!")

        if allow_methods:
            print_success(f"Allowed methods: {allow_methods}")

        if allow_headers:
            print_success(f"Allowed headers: {allow_headers}")

        if allow_credentials:
            print_success(f"Credentials allowed: {allow_credentials}")

        # Now send the actual request
        print(f"\n{Colors.YELLOW}2. Sending actual {method} request...{Colors.RESET}")

        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=5)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            print_error(f"Unsupported method: {method}")
            return

        print(f"Status Code: {response.status_code}")

        # Check CORS headers in actual response
        allow_origin_response = response.headers.get('Access-Control-Allow-Origin')
        if allow_origin_response:
            print_success(f"CORS header in response: {allow_origin_response}")
        else:
            print_warning("No CORS header in actual response")

        # Print response preview
        if response.status_code < 400:
            print_success(f"Request successful!")
            try:
                json_response = response.json()
                if isinstance(json_response, list):
                    print(f"Response: List with {len(json_response)} items")
                    if json_response:
                        print(f"First item: {json.dumps(json_response[0], indent=2)[:200]}...")
                elif isinstance(json_response, dict):
                    print(f"Response: {json.dumps(json_response, indent=2)[:300]}...")
            except:
                print(f"Response: {response.text[:200]}")
        else:
            print_error(f"Request failed!")
            print(f"Response: {response.text[:300]}")

    except requests.exceptions.ConnectionError:
        print_error("Connection failed! Is the API server running?")
    except requests.exceptions.Timeout:
        print_error("Request timed out!")
    except Exception as e:
        print_error(f"Error: {str(e)}")

def test_server_health(api_url: str):
    """Check if the API server is running."""
    print_header("Checking API Server Status")
    try:
        response = requests.get(f"{api_url}/docs", timeout=5)
        if response.status_code == 200:
            print_success(f"API server is running at {api_url}")
            return True
        else:
            print_warning(f"API server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API server at {api_url}")
        print_info("Make sure your FastAPI server is running:")
        print_info("  uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error checking server: {str(e)}")
        return False

def main():
    """Run CORS tests."""
    API_URL = "http://localhost:8000"

    print_header("E-Commerce API CORS Testing Tool")
    print_info(f"Target API: {API_URL}")
    print_info("This script will test CORS configuration by simulating requests from different origins.\n")

    # Check if server is running
    if not test_server_health(API_URL):
        return

    # Test 1: Allowed origin (React - port 3000)
    print_header("Test 1: Allowed Origin - React App (localhost:3000)")
    test_cors_request(
        api_url=API_URL,
        origin="http://localhost:3000",
        method="GET",
        endpoint="/products"
    )

    # Test 2: Allowed origin (Vite - port 5173)
    print_header("Test 2: Allowed Origin - Vite App (localhost:5173)")
    test_cors_request(
        api_url=API_URL,
        origin="http://localhost:5173",
        method="GET",
        endpoint="/products"
    )

    # Test 3: Allowed origin (Vue CLI - port 8080)
    print_header("Test 3: Allowed Origin - Vue App (localhost:8080)")
    test_cors_request(
        api_url=API_URL,
        origin="http://localhost:8080",
        method="GET",
        endpoint="/products"
    )

    # Test 4: Unauthorized origin (should be blocked)
    print_header("Test 4: Unauthorized Origin - Random Port (localhost:9999)")
    print_warning("This should be blocked by CORS policy")
    test_cors_request(
        api_url=API_URL,
        origin="http://localhost:9999",
        method="GET",
        endpoint="/products"
    )

    # Test 5: Different unauthorized domain
    print_header("Test 5: Unauthorized Origin - Different Domain")
    print_warning("This should be blocked by CORS policy")
    test_cors_request(
        api_url=API_URL,
        origin="http://evil-site.com",
        method="GET",
        endpoint="/products"
    )

    # Test 6: POST request with allowed origin
    print_header("Test 6: POST Request from Allowed Origin (localhost:3000)")
    print_info("Testing POST to /auth/login endpoint")
    test_cors_request(
        api_url=API_URL,
        origin="http://localhost:3000",
        method="POST",
        endpoint="/auth/login",
        data={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )

    # Test 7: Test with authentication header
    print_header("Test 7: Authenticated Request with CORS")
    print_info("This tests if Authorization header works with CORS")
    test_cors_request(
        api_url=API_URL,
        origin="http://localhost:3000",
        method="GET",
        endpoint="/auth/me",
        token="fake_token_for_testing"  # Will fail auth but tests CORS headers
    )

    # Summary
    print_header("CORS Testing Complete")
    print_info("Summary:")
    print_info("✅ Tests 1-3 should show 'CORS allowed' messages")
    print_info("❌ Tests 4-5 should either:")
    print_info("   - Show no Access-Control-Allow-Origin header, OR")
    print_info("   - Show Access-Control-Allow-Origin: * (if wildcard is enabled)")
    print_info("\nTo modify allowed origins, set CORS_ORIGINS environment variable:")
    print_info("  CORS_ORIGINS=http://localhost:3000,http://localhost:5173")
    print_info("\nOr edit app/core/config.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

