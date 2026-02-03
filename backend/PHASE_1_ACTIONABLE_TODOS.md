"""
PHASE 1 TODO LIST - ACTIONABLE & TRACKABLE
===========================================

COPY THIS INTO YOUR TODO TRACKER OR MARKDOWN APP!
You can check off items as you complete them.
"""

# ============================================================================
# BEFORE PHASE 1 STARTS
# ============================================================================

"""
PREREQUISITES (Should already be done):
    ✓ pytest installed (check: pip list | grep pytest)
    ✓ conftest.py created (tests/conftest.py exists)
    ✓ test_auth_basics.py created (tests/test_auth_basics.py exists)
    ✓ Understanding pytest basics (read PYTEST_BASICS_GUIDE.md sections 1-6)

If any NOT done:
    Go back and complete before Phase 1 starts!
"""

# ============================================================================
# PHASE 1: COMPLETE & ENHANCE USER SCHEMAS
# ============================================================================

"""
Estimated Total Time: 2-3 hours
Learning Focus: Pydantic validation, error handling, OpenAPI docs
Success Criteria: All tests pass, coverage > 90%, schemas production-ready

═══════════════════════════════════════════════════════════════════════════
TASK 1.1: AUDIT CURRENT AUTH SCHEMAS (20 minutes)
═══════════════════════════════════════════════════════════════════════

Goal: Understand current schema implementation and identify gaps

Subtasks:
    □ 1.1.1: Open file: app/schemas/auth.py
    □ 1.1.2: Read UserRegisterRequest class completely
    □ 1.1.3: Check: Is there a @field_validator for password? (search for @)
    □ 1.1.4: Check: What validation exists? (min_length, max_length, etc.)
    □ 1.1.5: Read UserLoginRequest class
    □ 1.1.6: Read current error/response schemas
    □ 1.1.7: Run existing tests: pytest tests/test_auth_basics.py::TestPasswordValidation -v
    □ 1.1.8: Note which tests PASS (validation works) vs FAIL (gaps found)
    □ 1.1.9: Read test_auth_basics.py comments to understand expected behavior
    □ 1.1.10: List validation gaps you found:
       - Password strength (uppercase, digit, special char?)
       - Phone validation (if present)
       - Error messages (clear? helpful?)

Success: You understand current state and know what's missing

Testing:
    pytest tests/test_auth_basics.py -m unit -v
    (Unit tests should all pass, integration tests may fail)

Time Check: Spent < 20 minutes? Good! Move to Task 1.2

═══════════════════════════════════════════════════════════════════════════
TASK 1.2: ADD PASSWORD STRENGTH VALIDATION (30 minutes)
═══════════════════════════════════════════════════════════════════════════

Goal: Implement production-grade password validation

Requirements:
    • Minimum 8 characters (already in requirements.txt?)
    • At least 1 UPPERCASE letter (A-Z)
    • At least 1 lowercase letter (a-z)
    • At least 1 digit (0-9)
    • At least 1 special character (@$!%*?&)
    • Clear error message for each rule

Subtasks:
    □ 2.1: Read about Pydantic field_validator in test docstrings
    □ 2.2: In app/schemas/auth.py, find UserRegisterRequest class
    □ 2.3: Add import: from pydantic import field_validator
    □ 2.4: Add method below password field:
       
       @field_validator('password')
       @classmethod
       def validate_password_strength(cls, v):
           '''Validate password meets strength requirements.'''
           if len(v) < 8:
               raise ValueError('Password must be at least 8 characters')
           if not any(c.isupper() for c in v):
               raise ValueError('Password must contain uppercase letter')
           if not any(c.islower() for c in v):
               raise ValueError('Password must contain lowercase letter')
           if not any(c.isdigit() for c in v):
               raise ValueError('Password must contain digit')
           if not any(c in '@$!%*?&' for c in v):
               raise ValueError('Password must contain special character (@$!%*?&)')
           return v

    □ 2.5: Also add to UserUpdateRequest if it has password field
    □ 2.6: Run tests: pytest tests/test_auth_basics.py::TestPasswordValidation -v
    □ 2.7: Check ALL TestPasswordValidation tests PASS:
       - test_weak_passwords_fail (parametrized - should have multiple cases)
       - All should show PASSED

    □ 2.8: If tests FAIL, read error message:
       - "Password must be at least 8 characters" → Your validator triggered!
       - "Looks like the message..." → Check error message format
       - Adjust code and re-run

    □ 2.9: Also verify registration test still works:
       pytest tests/test_auth_basics.py::TestAuthRegisterEndpoint::test_register_success -v

Success: TestPasswordValidation tests all PASS

Testing:
    pytest tests/test_auth_basics.py::TestPasswordValidation -v
    pytest tests/test_auth_basics.py::TestAuthRegisterEndpoint -v

Time Check: Spent ~30 minutes? Good! Move to Task 1.3

═══════════════════════════════════════════════════════════════════════════
TASK 1.3: ADD PHONE NUMBER VALIDATION (25 minutes)
═══════════════════════════════════════════════════════════════════════════

Goal: Accept and validate phone numbers in multiple formats

Requirements:
    • Make phone field optional (can be None)
    • Accept formats: +1234567890, 123-456-7890, (123) 456-7890, 1234567890
    • Validate length: 10-15 digits (after removing non-digits)
    • Return None if empty/None (don't validate empty optional field)
    • Clear error message

Subtasks:
    □ 3.1: Open app/schemas/auth.py
    □ 3.2: Find phone field in UserRegisterRequest
    □ 3.3: Make sure it's: Optional[str] = None
    □ 3.4: Add validator below password validator:
       
       import re
       
       @field_validator('phone', mode='before')
       @classmethod
       def validate_phone(cls, v):
           '''Validate phone number format.'''
           if v is None or v == '':
               return None
           # Remove non-digit characters except +
           digits_only = re.sub(r'[^0-9+]', '', v)
           # Remove leading + for digit count
           digit_count = len(digits_only.replace('+', ''))
           
           if digit_count < 10 or digit_count > 15:
               raise ValueError('Phone must have 10-15 digits')
           return v

    □ 3.5: Run tests: pytest tests/test_auth_basics.py -v
    □ 3.6: Verify registration still works with phone:
       pytest tests/test_auth_basics.py::TestAuthRegisterEndpoint::test_register_success -v
    □ 3.7: Test with invalid phone (optional - not in current tests):
       Open browser: http://localhost:8000/docs
       Try Register with: phone: "invalid"
       Should see error message

Success: Phone validation works, registration still passes

Testing:
    pytest tests/test_auth_basics.py -v

Time Check: Spent ~25 minutes? Good! Move to Task 1.4

═══════════════════════════════════════════════════════════════════════════
TASK 1.4: CREATE ERROR RESPONSE SCHEMAS (20 minutes)
═══════════════════════════════════════════════════════════════════════════

Goal: Define consistent error response structure

Requirements:
    • ValidationErrorResponse (for 422 validation errors)
    • AuthErrorResponse (for 401 auth errors)
    • ErrorDetail (individual error field info)
    • Clear examples in docstrings

Subtasks:
    □ 4.1: Open app/schemas/common.py
    □ 4.2: Add at top of file:
       
       from typing import List
       from pydantic import BaseModel
       
       class ErrorDetail(BaseModel):
           '''Detail of a single validation error.'''
           field: str
           message: str
           code: str
           
           class Config:
               json_schema_extra = {
                   "example": {
                       "field": "password",
                       "message": "Password must contain uppercase letter",
                       "code": "WEAK_PASSWORD"
                   }
               }
       
       class ValidationErrorResponse(BaseModel):
           '''Validation error response (422).'''
           error: str = "VALIDATION_ERROR"
           status_code: int = 422
           errors: List[ErrorDetail]
           
           class Config:
               json_schema_extra = {
                   "example": {
                       "error": "VALIDATION_ERROR",
                       "status_code": 422,
                       "errors": [
                           {
                               "field": "password",
                               "message": "Password must contain uppercase letter",
                               "code": "WEAK_PASSWORD"
                           },
                           {
                               "field": "email",
                               "message": "Invalid email format",
                               "code": "INVALID_EMAIL"
                           }
                       ]
                   }
               }
       
       class AuthErrorResponse(BaseModel):
           '''Authentication error response (401, 403).'''
           error: str
           detail: str
           status_code: int
           
           class Config:
               json_schema_extra = {
                   "example": {
                       "error": "INVALID_CREDENTIALS",
                       "detail": "Email or password incorrect",
                       "status_code": 401
                   }
               }

    □ 4.3: Save file
    □ 4.4: Check there are no import errors:
       python -c "from app.schemas.common import ValidationErrorResponse"
    □ 4.5: These will be used in Phase 2 (endpoints)
    □ 4.6: Run existing tests to ensure no breakage:
       pytest tests/test_auth_basics.py -v

Success: Error schemas created, no import errors

Testing:
    pytest tests/test_auth_basics.py -v

Time Check: Spent ~20 minutes? Good! Move to Task 1.5

═══════════════════════════════════════════════════════════════════════════
TASK 1.5: ADD OPENAPI DOCUMENTATION TO SCHEMAS (25 minutes)
═══════════════════════════════════════════════════════════════════════════

Goal: Make API documentation clear in Swagger UI (/docs)

Requirements:
    • Add descriptions to all fields
    • Add examples to fields
    • Add json_schema_extra with full examples to request classes
    • Swagger UI should show validation rules and examples

Subtasks:
    □ 5.1: Open app/schemas/auth.py
    □ 5.2: Find UserRegisterRequest class
    □ 5.3: Update email field:
       
       email: EmailStr = Field(
           ...,
           description="User email address (must be valid)",
           example="john.doe@example.com",
           title="Email"
       )

    □ 5.4: Update password field:
       
       password: str = Field(
           ...,
           min_length=8,
           description="Strong password (8+ chars, uppercase, lowercase, digit, special char @$!%*?&)",
           example="SecurePass123!",
           title="Password",
           json_schema_extra={
               "pattern": "(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*?&])"
           }
       )

    □ 5.5: Update first_name field:
       
       first_name: str = Field(
           ...,
           min_length=1,
           max_length=50,
           description="User's first name",
           example="John",
           title="First Name"
       )

    □ 5.6: Update last_name field:
       
       last_name: str = Field(
           ...,
           min_length=1,
           max_length=50,
           description="User's last name",
           example="Doe",
           title="Last Name"
       )

    □ 5.7: Update phone field (if present):
       
       phone: Optional[str] = Field(
           None,
           description="Phone number (+1234567890 or 123-456-7890 format)",
           example="+1234567890",
           title="Phone (Optional)"
       )

    □ 5.8: Update role field:
       
       role: Literal["USER", "BROKER", "OWNER", "ADMIN"] = Field(
           "USER",
           description="User role (USER, BROKER, OWNER, or ADMIN)",
           example="USER",
           title="Role"
       )

    □ 5.9: Add Config to UserRegisterRequest with example:
       
       class Config:
           json_schema_extra = {
               "example": {
                   "email": "john.doe@example.com",
                   "password": "SecurePass123!",
                   "first_name": "John",
                   "last_name": "Doe",
                   "phone": "+1234567890",
                   "role": "USER"
               }
           }

    □ 5.10: Do the same for UserLoginRequest:
       - email: with description and example
       - password: with description

    □ 5.11: Save all changes
    □ 5.12: Start server: cd backend && uvicorn app.main:app --reload
    □ 5.13: Visit http://localhost:8000/docs
    □ 5.14: Click on "POST /auth/register"
    □ 5.15: Check:
       - All fields have descriptions
       - All fields show examples
       - Error responses are documented
       - Everything looks professional

    □ 5.16: Test the endpoint in Swagger UI:
       - Click "Try it out"
       - Pre-filled example data should appear
       - Click "Execute"
       - Should succeed (201 Created)

Success: Swagger UI shows complete documentation with examples

Testing:
    pytest tests/test_auth_basics.py -v
    (All tests should still pass)
    
    Visual check: http://localhost:8000/docs
    (Should look professional and clear)

Time Check: Spent ~25 minutes? Good! Move to final test

═══════════════════════════════════════════════════════════════════════════
FINAL: RUN ALL TESTS & VERIFY SUCCESS (10 minutes)
═══════════════════════════════════════════════════════════════════════════

Goal: Confirm Phase 1 complete and ready for Phase 2

Subtasks:
    □ F.1: Run all auth tests:
       pytest tests/test_auth_basics.py -v

    □ F.2: Check output:
       ✓ All tests should show PASSED (green)
       ✗ If any FAILED, debug and fix before moving on

    □ F.3: Run with coverage:
       pytest tests/test_auth_basics.py --cov=app.schemas --cov-report=term-missing

    □ F.4: Check coverage:
       ✓ Should show coverage > 90%
       ✗ If < 80%, you missed some validation rules

    □ F.5: Generate HTML coverage report:
       pytest tests/test_auth_basics.py --cov=app --cov-report=html
       Open: htmlcov/index.html in browser
       Check which lines are red (not tested)

    □ F.6: Final checklist:
       ✓ All tests PASS
       ✓ Coverage > 90%
       ✓ Can explain each validation rule
       ✓ Swagger UI looks good
       ✓ Ready to move to Phase 2

Success Criteria Met:
    ✓ Password validation works (8+ chars, upper, lower, digit, special)
    ✓ Phone validation works (accepts multiple formats)
    ✓ Error schemas defined (ErrorDetail, ValidationErrorResponse, AuthErrorResponse)
    ✓ OpenAPI docs complete (Swagger UI looks professional)
    ✓ All tests pass (pytest tests/test_auth_basics.py -v)
    ✓ Coverage > 90% (--cov=app.schemas)

═══════════════════════════════════════════════════════════════════════════
PHASE 1 COMPLETE! 🎉
═══════════════════════════════════════════════════════════════════════════

Congratulations! You've:
    ✓ Set up pytest for your project
    ✓ Created test fixtures and examples
    ✓ Implemented production-grade schema validation
    ✓ Created error response schemas
    ✓ Documented everything with OpenAPI/Swagger
    ✓ Achieved 90%+ test coverage
    ✓ Learned Pydantic validators and Pytest basics

NEXT: Move to Phase 2 (User CRUD with error handling)
     Follow: PHASE_1_DETAILED_TODOS.md Phase 2 section
"""

print("=" * 70)
print("PHASE 1 TODO LIST CREATED!")
print("=" * 70)
print()
print("📋 FOLLOW THIS STRUCTURE:")
print("   Task 1.1: Audit Schemas (20 min)")
print("   Task 1.2: Password Validation (30 min)")
print("   Task 1.3: Phone Validation (25 min)")
print("   Task 1.4: Error Schemas (20 min)")
print("   Task 1.5: OpenAPI Docs (25 min)")
print("   Final: Test & Verify (10 min)")
print()
print("⏱️  TOTAL: ~2.5 hours")
print()
print("🚀 START NOW:")
print("   cd backend")
print("   pytest tests/test_auth_basics.py -v")
print()
print("Good luck! 💪")
