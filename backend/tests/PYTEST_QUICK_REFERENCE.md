"""
PYTEST QUICK REFERENCE CARD
============================

Save this for quick lookups while coding!
"""

# ============================================================================
# COMMAND QUICK REFERENCE
# ============================================================================

"""
RUN TESTS:
    pytest                              All tests
    pytest -v                           Verbose (show names)
    pytest -s                           Show print output
    pytest -x                           Stop on first failure
    pytest --lf                         Re-run last failed
    pytest -k "login"                   Run tests with "login" in name
    pytest -m unit                      Only @pytest.mark.unit tests
    pytest --cov=app                    Coverage report
    pytest --cov=app --cov-report=html  HTML coverage report

OUR TESTS:
    pytest tests/test_auth_basics.py -v                    All auth tests
    pytest tests/test_auth_basics.py::TestPasswordHashing  One class
    pytest tests/test_auth_basics.py -m unit               Only unit tests
    pytest tests/test_auth_basics.py -m integration        Only integration
"""

# ============================================================================
# ASSERTION PATTERNS
# ============================================================================

"""
BASIC ASSERTIONS:
    assert value == expected
    assert value is True
    assert value is False
    assert value is None
    assert len(items) == 3
    assert isinstance(obj, str)
    assert "substring" in "string"
    assert value > 10
    assert value in [1, 2, 3]

RESPONSE ASSERTIONS:
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert "password" not in response.json()
    assert "access_token" in response.json()

EXCEPTION ASSERTIONS:
    with pytest.raises(ValueError):
        do_something()
    
    with pytest.raises(ValueError, match="email"):
        do_something_with_bad_email()
"""

# ============================================================================
# FIXTURE PATTERNS
# ============================================================================

"""
CREATING FIXTURES (in conftest.py):
    @pytest.fixture
    def test_user():
        return User(email="test@example.com")
    
    @pytest.fixture(scope="function")  # New per test
    @pytest.fixture(scope="class")     # Shared in class
    @pytest.fixture(scope="module")    # Shared in file
    @pytest.fixture(scope="session")   # Shared for all

USING FIXTURES (in tests):
    def test_something(test_user):
        assert test_user.email == "test@example.com"
    
    def test_multiple_fixtures(client, test_user, test_db):
        # Can use many fixtures at once!
        pass

FIXTURE DEPENDENCY:
    @pytest.fixture
    def test_user_in_db(test_db, test_user_data):
        # Depends on test_db and test_user_data fixtures
        user = User(**test_user_data)
        test_db.add(user)
        test_db.commit()
        return user
"""

# ============================================================================
# TEST STRUCTURE
# ============================================================================

"""
BASIC TEST:
    def test_something(client, test_user):
        # ARRANGE: Setup
        data = {"email": "test@example.com"}
        
        # ACT: Do the thing
        response = client.post("/auth/register", json=data)
        
        # ASSERT: Check result
        assert response.status_code == 201

TEST CLASS:
    class TestUserRegistration:
        def test_register_success(self, client):
            # ...
        
        def test_register_duplicate_email(self, client):
            # ...

PARAMETRIZED TEST:
    @pytest.mark.parametrize("email", ["test@example.com", "bad@email"])
    def test_email(client, email):
        response = client.post("/auth/register", json={"email": email})
        # Runs twice with different emails
"""

# ============================================================================
# FASTAPI TESTCLIENT PATTERNS
# ============================================================================

"""
MAKE REQUESTS:
    client.get("/api/users/1")
    client.post("/auth/login", json={"email": "...", "password": "..."})
    client.put("/api/users/1", json={"first_name": "Jane"})
    client.delete("/api/users/1")

WITH HEADERS:
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)

QUERY PARAMETERS:
    response = client.get("/users?skip=0&limit=10")

RESPONSE PROPERTIES:
    response.status_code       # 200, 404, 401, etc.
    response.json()            # Parse JSON
    response.text              # Raw text
    response.headers           # Response headers

HTTP STATUS CODES:
    200 OK
    201 Created
    400 Bad Request
    401 Unauthorized
    403 Forbidden
    404 Not Found
    422 Unprocessable Entity (validation error)
    500 Internal Server Error
"""

# ============================================================================
# PYTEST MARKS
# ============================================================================

"""
DEFINE MARKS (in conftest.py):
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "auth: Auth tests")

USE MARKS (in tests):
    @pytest.mark.unit
    def test_password_hashing():
        ...
    
    @pytest.mark.integration
    def test_login_endpoint():
        ...
    
    @pytest.mark.auth
    @pytest.mark.slow
    def test_multiple_marks():
        ...

RUN WITH MARKS:
    pytest -m unit                  # Only unit tests
    pytest -m integration           # Only integration
    pytest -m "unit or auth"        # Unit OR auth
    pytest -m "not slow"            # Skip slow tests
"""

# ============================================================================
# COMMON PATTERNS IN OUR PROJECT
# ============================================================================

"""
UNIT TEST (fast, no DB):
    @pytest.mark.unit
    def test_hash_password_creates_different_hash():
        password = "MyPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

INTEGRATION TEST (with HTTP + DB):
    @pytest.mark.integration
    def test_register_success(client, test_user_data):
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 201

ERROR TEST (checking error handling):
    def test_login_wrong_password(client, test_user_in_db):
        response = client.post("/auth/login", json={
            "email": test_user_in_db.email,
            "password": "WrongPassword"
        })
        assert response.status_code == 401

VALIDATION TEST (checking input validation):
    def test_register_invalid_email(client):
        response = client.post("/auth/register", json={
            "email": "notanemail",  # Invalid!
            "password": "SecurePass123!",
            "first_name": "John"
        })
        assert response.status_code == 422

AUTH TEST (checking protected endpoints):
    def test_protected_endpoint_without_token(client):
        response = client.get("/users/me")  # No token
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(client, valid_token):
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200
"""

# ============================================================================
# DEBUGGING & TROUBLESHOOTING
# ============================================================================

"""
RUN WITH DEBUG OUTPUT:
    pytest tests/test_auth_basics.py -v -s
    # -v: verbose (show test names)
    # -s: show print() output

USE DEBUGGER:
    def test_something():
        value = do_something()
        breakpoint()  # Pauses here, open Python debugger
        assert value == expected

COMMON ERRORS:

ImportError: No module named 'app'
    -> Run pytest from backend directory:
       cd backend
       pytest

FAILED: E fixture "client" not found
    -> Check conftest.py exists in tests/ directory

AssertionError: 201 != 422
    -> Check request data (email format, password, etc.)

TypeError: test_user() missing 1 required positional argument: 'self'
    -> Remove class wrapper or make test a method of class

Test passes locally but fails in CI
    -> Might need to set DATABASE_URL env variable
"""

# ============================================================================
# OUR PROJECT STRUCTURE
# ============================================================================

"""
backend/
    pyproject.toml              # pytest config here
    requirements.txt            # pytest already installed
    tests/
        __init__.py
        conftest.py             # SHARED FIXTURES ← START HERE
        test_auth_basics.py     # EXAMPLE TESTS
        PYTEST_BASICS_GUIDE.md  # FULL GUIDE
    app/
        main.py                 # FastAPI app
        api/
            v1/
                auth.py         # Auth endpoints
                users.py        # User endpoints
        schemas/
            auth.py             # Schemas to test
        core/
            security.py         # Password/token functions

PHASE_1_DETAILED_TODOS.md       # ← FOLLOW THIS!

KEY FILES TO READ:
    tests/conftest.py           → Fixtures and DB setup
    tests/test_auth_basics.py   → Working test examples
    tests/PYTEST_BASICS_GUIDE.md → Full pytest tutorial
"""

# ============================================================================
# WORKFLOW
# ============================================================================

"""
TYPICAL TEST-DRIVEN WORKFLOW:

1. Read Phase 1 TODO
2. Write tests first (in test_auth_basics.py)
3. Run tests (they fail - RED)
4. Update schemas (in app/schemas/auth.py)
5. Run tests again (they pass - GREEN)
6. Refactor code if needed
7. Commit changes

USEFUL COMMAND SEQUENCE:

cd backend
pytest tests/test_auth_basics.py -v                 # See what fails
pytest tests/test_auth_basics.py::TestPasswordHashing -v   # One test class
pytest tests/test_auth_basics.py -k "register" -v  # One type of test
pytest tests/test_auth_basics.py --lf              # Re-run failures
pytest tests/test_auth_basics.py --cov=app.schemas # Coverage
"""

print("✓ Pytest Quick Reference Ready!")
print("✓ Save this for quick lookups")
