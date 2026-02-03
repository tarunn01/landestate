"""
FILE: tests/PYTEST_BASICS_GUIDE.md

COMPREHENSIVE PYTEST LEARNING GUIDE
====================================

This guide teaches pytest fundamentals for testing FastAPI applications.
"""

# ============================================================================
# 1. PYTEST BASICS
# ============================================================================

"""
WHAT IS PYTEST?
- Python testing framework (like JUnit for Java)
- Makes writing tests easy and fun
- Auto-discovers and runs tests
- Clear, readable assertions

WHY PYTEST?
✓ Simple assertion syntax: assert x == y (not assert_equals)
✓ Powerful fixtures (reusable test setup)
✓ Great error messages
✓ Easy to parametrize tests
✓ Built-in test discovery
"""

# ============================================================================
# 2. RUNNING PYTEST
# ============================================================================

"""
BASIC COMMANDS:

1. Run all tests:
   pytest

2. Run specific test file:
   pytest tests/test_auth_basics.py

3. Run specific test class:
   pytest tests/test_auth_basics.py::TestPasswordHashing

4. Run specific test:
   pytest tests/test_auth_basics.py::TestPasswordHashing::test_hash_password_creates_different_hash

5. Verbose output (show test names):
   pytest -v

6. Show print statements:
   pytest -s

7. Run with coverage report:
   pytest --cov=app --cov-report=html

8. Run only tests with specific mark:
   pytest -m unit           # Only unit tests
   pytest -m integration    # Only integration tests
   pytest -m auth          # Only auth tests

9. Stop after first failure:
   pytest -x

10. Run last failed tests:
    pytest --lf
"""

# ============================================================================
# 3. TEST STRUCTURE
# ============================================================================

"""
ANATOMY OF A TEST:

def test_something(fixtures_here):
    # ARRANGE: Set up test data
    user = User(email="test@example.com")
    
    # ACT: Perform the action being tested
    result = some_function(user)
    
    # ASSERT: Check that result is correct
    assert result.success is True

THREE PARTS OF EVERY TEST:
1. Arrange (setup)
2. Act (do the thing)
3. Assert (check results)
"""

# ============================================================================
# 4. ASSERTIONS (Checking Results)
# ============================================================================

"""
BASIC ASSERTIONS:

assert value is True           # Value is True
assert value is False          # Value is False
assert value == expected       # Value equals expected
assert value != expected       # Value does not equal expected
assert value > 10              # Value greater than 10
assert value in [1, 2, 3]      # Value in list
assert isinstance(value, str)  # Value is a string

EXCEPTION ASSERTIONS:

# Check that function raises an error
with pytest.raises(ValueError):
    some_function_that_raises()

# Check error message
with pytest.raises(ValueError, match="email"):
    some_function_with_bad_email()

COMPARISON OPERATORS:
==  equals
!=  not equals
>   greater than
<   less than
>=  greater or equal
<=  less or equal
in  is contained in
"""

# ============================================================================
# 5. FIXTURES (Reusable Setup)
# ============================================================================

"""
WHAT ARE FIXTURES?
- Functions that provide test data/setup
- Reusable across multiple tests
- Automatic cleanup

FIXTURE SCOPES:
- function: New fixture for each test (default)
- class: Shared for all tests in class
- module: Shared for all tests in file
- session: Shared for entire test session

@pytest.fixture(scope="function")
def test_user():
    user = User(email="test@example.com")
    yield user  # Provide to test
    # Cleanup happens after test

# Usage in test:
def test_something(test_user):
    assert test_user.email == "test@example.com"

FIXTURE DEPENDENCY:
Fixtures can depend on other fixtures:

@pytest.fixture
def test_db():
    return create_database()

@pytest.fixture
def test_user(test_db):  # Depends on test_db
    return create_user(test_db)

def test_something(test_user):  # Automatically gets test_db too
    assert test_user is not None
"""

# ============================================================================
# 6. TEST CLASSES (Organizing Tests)
# ============================================================================

"""
USE CLASSES TO ORGANIZE RELATED TESTS:

class TestUserRegistration:
    \"\"\"All registration-related tests.\"\"\"
    
    def test_register_success(self, client):
        # ...
    
    def test_register_duplicate_email(self, client):
        # ...
    
    def test_register_invalid_email(self, client):
        # ...

BENEFITS:
✓ Logical grouping
✓ Easier to navigate
✓ Can share fixtures at class level
✓ Better organization as project grows

Pytest runs tests in classes in order (top to bottom):
- test_register_success
- test_register_duplicate_email
- test_register_invalid_email
"""

# ============================================================================
# 7. PARAMETRIZED TESTS (Multiple Test Cases)
# ============================================================================

"""
RUN SAME TEST WITH MULTIPLE INPUTS:

@pytest.mark.parametrize("input,expected", [
    ("test", True),
    ("", False),
    (None, False),
])
def test_validate(input, expected):
    assert is_valid(input) == expected

This creates 3 separate tests with different inputs.

PARAMETRIZE MULTIPLE ARGUMENTS:

@pytest.mark.parametrize("email", [
    "valid@example.com",
    "another@test.com",
    "bad-email",
])
def test_email_validation(email):
    # Runs 3 times with different emails
    result = validate_email(email)
    ...

PARAMETRIZE WITH FIXTURE:

@pytest.mark.parametrize("password", [
    "weak",
    "short",
    "123456",
])
def test_password_strength(password, test_user):
    # test_user fixture + parametrized password
    ...
"""

# ============================================================================
# 8. MARKS (Categorizing Tests)
# ============================================================================

"""
USE MARKS TO CATEGORIZE TESTS:

@pytest.mark.unit
def test_password_hashing():
    # Fast test, no I/O
    ...

@pytest.mark.integration
def test_login_endpoint():
    # Uses database and HTTP
    ...

@pytest.mark.slow
def test_large_data_processing():
    # Takes a long time
    ...

@pytest.mark.auth
def test_protected_endpoint():
    # Authentication-related
    ...

RUN ONLY TESTS WITH MARK:
pytest -m unit              # Only unit tests
pytest -m integration       # Only integration tests
pytest -m "not slow"        # Skip slow tests
pytest -m "unit or auth"    # Unit tests OR auth tests

BENEFITS:
✓ Organize tests logically
✓ Run subsets (e.g., fast tests only)
✓ CI/CD pipeline (fast tests on every push, slow tests nightly)
"""

# ============================================================================
# 9. CONFTEST.PY (Shared Configuration)
# ============================================================================

"""
conftest.py PURPOSE:
- Centralized fixture definitions
- Shared test configuration
- Database setup/teardown
- Mock external services

LOCATION:
backend/tests/conftest.py  <- pytest auto-discovers this

WHAT GOES IN CONFTEST:
✓ Global fixtures
✓ Database setup
✓ Mock clients
✓ Test data factories
✓ Custom pytest hooks

FIXTURE AVAILABILITY:
Fixtures defined in conftest.py are available to ALL tests.

@pytest.fixture
def test_db():
    # Now available to any test:
    # test_auth.py, test_users.py, etc.
    ...

STRUCTURE:
conftest.py can have multiple conftest.py files:
backend/conftest.py          # Available to all tests
backend/tests/conftest.py    # Available to tests/ directory
backend/tests/api/conftest.py # Available to tests/api/ directory
"""

# ============================================================================
# 10. TESTING FASTAPI ENDPOINTS
# ============================================================================

"""
TESTCLIENT FOR HTTP REQUESTS:

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# GET request
response = client.get("/api/users/1")
assert response.status_code == 200

# POST request
response = client.post("/api/users", json={
    "email": "test@example.com",
    "password": "SecurePass123"
})
assert response.status_code == 201

# PUT request
response = client.put("/api/users/1", json={"first_name": "Jane"})

# DELETE request
response = client.delete("/api/users/1")

# Request with headers
response = client.get("/api/users/me", headers={
    "Authorization": f"Bearer {token}"
})

# Request with query parameters
response = client.get("/api/users?skip=0&limit=10")

RESPONSE OBJECT:
response.status_code   # HTTP status (200, 404, 500, etc.)
response.json()        # Parse JSON response
response.text          # Raw text response
response.content       # Raw bytes

STATUS CODES:
200 OK
201 Created
400 Bad Request (invalid input)
401 Unauthorized (auth required)
403 Forbidden (no permission)
404 Not Found
422 Unprocessable Entity (validation failed)
500 Internal Server Error
"""

# ============================================================================
# 11. MOCKING AND DEPENDENCY OVERRIDES
# ============================================================================

"""
OVERRIDE FASTAPI DEPENDENCIES FOR TESTING:

In your code:
from app.core.database import get_db

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

In test (conftest.py):
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield SessionLocal()
    app.dependency_overrides.clear()

Now your tests use in-memory SQLite instead of real database!

MOCK EXTERNAL SERVICES:
from unittest.mock import patch

@patch("app.services.email.send_email")
def test_registration_sends_email(mock_send_email, client):
    response = client.post("/auth/register", json={...})
    
    # Check that send_email was called
    assert mock_send_email.called
    assert mock_send_email.call_count == 1
"""

# ============================================================================
# 12. TEST DATABASE PATTERNS
# ============================================================================

"""
IN-MEMORY DATABASE:
Fastest for testing, no I/O

engine = create_engine("sqlite:///:memory:")

BENEFITS:
✓ Super fast
✓ No cleanup needed
✓ Tests run in parallel
✓ Isolated (each test gets new DB)

FIXTURE EXAMPLE:
@pytest.fixture(scope="function")
def test_db():
    # New database for EACH test
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield SessionLocal()
    app.dependency_overrides.clear()

WHY scope="function"?
- Each test gets FRESH database
- Prevents tests from interfering with each other
- Test isolation = reliable tests
"""

# ============================================================================
# 13. EXAMPLE TEST PATTERNS
# ============================================================================

"""
PATTERN 1: HAPPY PATH TEST
def test_login_success(client, test_user_in_db):
    response = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "SecurePass123!"
    })
    
    assert response.status_code == 200
    assert response.json()["access_token"]

PATTERN 2: ERROR CASE TEST
def test_login_wrong_password(client, test_user_in_db):
    response = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "WrongPassword"
    })
    
    assert response.status_code == 401

PATTERN 3: VALIDATION TEST
def test_register_invalid_email(client):
    response = client.post("/auth/register", json={
        "email": "not-an-email",  # Invalid!
        "password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe"
    })
    
    assert response.status_code == 422  # Validation error

PATTERN 4: PARAMETRIZED TEST
@pytest.mark.parametrize("email", [
    "invalid",
    "@nodomain",
    "spaces in@email.com"
])
def test_invalid_emails(client, email):
    response = client.post("/auth/register", json={
        "email": email,
        "password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe"
    })
    
    assert response.status_code == 422
"""

# ============================================================================
# 14. COVERAGE REPORT
# ============================================================================

"""
WHAT IS CODE COVERAGE?
Percentage of your code that tests exercise.

Run with coverage:
pytest --cov=app --cov-report=html

This creates:
- htmlcov/index.html (open in browser)
- Shows which lines are tested/untested

UNDERSTANDING COVERAGE:
- 100% coverage: Every line run by tests
- 80% coverage: 20% of code untested
- Red lines: Not tested
- Green lines: Tested

LIMITATIONS:
- 100% coverage doesn't mean tests are good
- Still need to test edge cases and errors
- Test quality > test quantity

AIM FOR:
- 80%+ coverage on critical code (auth, payments)
- 60%+ coverage overall
- Every error path tested
"""

# ============================================================================
# 15. DEBUGGING TESTS
# ============================================================================

"""
SHOW PRINT STATEMENTS:
pytest -s

Your print() statements appear in output

USE DEBUGGER:
def test_something():
    value = do_something()
    breakpoint()  # Pauses execution here
    assert value == expected

pytest will drop into Python debugger

VERBOSE OUTPUT:
pytest -v
Shows which test passed/failed

LAST FAILED TESTS:
pytest --lf
Re-run only tests that failed last run

STOP AT FIRST FAILURE:
pytest -x
Useful when many tests fail

CHECK ONE TEST:
pytest tests/test_auth_basics.py::TestPasswordHashing::test_hash_password_creates_different_hash -v -s
"""

# ============================================================================
# 16. BEST PRACTICES
# ============================================================================

"""
✓ ONE ASSERTION per test (usually)
✓ Clear test names: test_register_with_duplicate_email
✓ Use fixtures for setup
✓ Test error cases, not just happy path
✓ Use marks to categorize tests
✓ Keep tests simple and readable
✓ Use parametrize for multiple test cases
✓ Test edge cases (empty string, None, negative numbers)
✓ Aim for 80%+ coverage
✓ Run tests frequently during development

✗ DON'T share state between tests
✗ DON'T use sleep() (makes tests slow)
✗ DON'T test implementation details
✗ DON'T put everything in one test
✗ DON'T use real external services
"""

# ============================================================================
# 17. PYTEST.INI CONFIGURATION
# ============================================================================

"""
Your pyproject.toml has:

[tool.pytest.ini_options]
testpaths = ["tests"]              # Where to find tests
python_files = "test_*.py"         # Test file naming pattern
addopts = "-v --cov=app --cov-report=html --cov-report=term-missing"
                                   # Default options when running pytest
asyncio_mode = "auto"              # For async tests

This means:
pytest                 # Finds and runs tests/ directory
                       # Shows verbose output
                       # Generates coverage report
"""

# ============================================================================
# 18. QUICK REFERENCE
# ============================================================================

"""
QUICK COMMAND REFERENCE:

pytest                      Run all tests
pytest -v                   Verbose (show test names)
pytest -s                   Show print output
pytest tests/test_auth_basics.py    Run specific file
pytest -k "login"           Run tests with "login" in name
pytest -m unit              Run tests marked @pytest.mark.unit
pytest --lf                 Re-run last failed
pytest -x                   Stop on first failure
pytest --cov=app            Generate coverage report
pytest --cov=app --cov-report=html   HTML coverage report

ASSERTION CHEAT SHEET:

assert value == expected
assert value is True
assert value is None
assert isinstance(value, str)
assert len(list) > 0
assert "substring" in "string"
with pytest.raises(Exception):
    do_something()

FIXTURE DECORATOR:

@pytest.fixture
def my_fixture():
    return "some value"

@pytest.fixture(scope="function")  # New per test
@pytest.fixture(scope="class")     # Shared in class
@pytest.fixture(scope="module")    # Shared in file
@pytest.fixture(scope="session")   # Shared for all
"""

print("✓ Pytest Basics Guide Ready!")
print("✓ Check test_auth_basics.py for working examples")
print("✓ Run: pytest tests/test_auth_basics.py -v")
