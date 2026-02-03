"""
FILE: PHASE_1_DETAILED_TODOS.md

PHASE 1: COMPLETE & ENHANCE USER SCHEMAS WITH VALIDATION
========================================================

Estimated Time: 2-3 hours
Learning Focus: Data validation, error handling, Pydantic

This phase focuses on making your schemas production-grade with:
- Comprehensive validation rules
- Custom error messages
- Error response schemas
- Edge case handling
"""

# ============================================================================
# PHASE 1 BREAKDOWN: 5 MAIN TASKS
# ============================================================================

"""
TASK 1.1: Audit Current Auth Schemas
- File: backend/app/schemas/auth.py
- Duration: 20 minutes
- Subtasks:
  □ Read current UserRegisterRequest schema
  □ Read current UserLoginRequest schema
  □ Read current LoginResponse schema
  □ Identify missing validation rules
  □ Check for password strength validation
  □ Check for email format validation
  □ Check for required field validation
  
Learning Goals:
  - Understand what Pydantic validators are
  - See what validation already exists
  - Identify gaps

Run After:
  pytest tests/test_auth_basics.py::TestPasswordValidation -v


TASK 1.2: Add Comprehensive Password Validation
- File: backend/app/schemas/auth.py
- Duration: 30 minutes
- Subtasks:
  □ Add password strength validator
  □ Check minimum 8 characters (already done?)
  □ Check at least 1 uppercase letter
  □ Check at least 1 lowercase letter
  □ Check at least 1 digit
  □ Check at least 1 special character (@$!%*?&)
  □ Add clear error messages
  □ Test with test_auth_basics.py

Learning Goals:
  - Create custom Pydantic validators
  - Use @field_validator decorator
  - Return meaningful error messages

Code Pattern:
  from pydantic import field_validator
  
  class UserRegisterRequest(BaseModel):
      password: str
      
      @field_validator('password')
      @classmethod
      def validate_password_strength(cls, v):
          if len(v) < 8:
              raise ValueError('At least 8 characters')
          if not any(c.isupper() for c in v):
              raise ValueError('At least 1 uppercase letter')
          # ... more checks
          return v

Run After:
  pytest tests/test_auth_basics.py::TestPasswordValidation -v


TASK 1.3: Add Phone Number Validation
- File: backend/app/schemas/auth.py
- Duration: 25 minutes
- Subtasks:
  □ Add phone validator (optional field)
  □ Accept formats: +1234567890, 123-456-7890, (123) 456-7890
  □ Validate length (10-15 digits)
  □ Add clear error messages
  □ Make phone field optional in UserRegisterRequest
  □ Test validation

Learning Goals:
  - Work with regex in validators
  - Handle optional fields
  - Format validation

Code Pattern:
  import re
  
  @field_validator('phone', mode='before')
  @classmethod
  def validate_phone(cls, v):
      if v is None or v == "":
          return None
      phone_pattern = r'^\\+?1?\\d{9,15}$'
      if not re.match(phone_pattern, v.replace('-', '').replace(' ', '')):
          raise ValueError('Invalid phone format')
      return v

Run After:
  pytest tests/test_auth_basics.py -v


TASK 1.4: Create Error Response Schemas
- File: backend/app/schemas/common.py (or auth.py)
- Duration: 20 minutes
- Subtasks:
  □ Create ValidationErrorResponse schema
    □ Create AuthErrorResponse schema
  □ Create ErrorDetail schema (for error field messages)
  □ Add examples to docstrings
  □ Document error codes (INVALID_EMAIL, WEAK_PASSWORD, etc.)

Learning Goals:
  - Design error response structures
  - Understand HTTP error conventions
  - Document error responses

Code Pattern:
  class ErrorDetail(BaseModel):
      field: str
      message: str
      code: str
      
  class ValidationErrorResponse(BaseModel):
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
                      }
                  ]
              }
          }

Run After:
  Review in test_auth_basics.py error test cases


TASK 1.5: Add OpenAPI Documentation to Schemas
- File: backend/app/schemas/auth.py
- Duration: 25 minutes
- Subtasks:
  □ Add Field descriptions to all fields
  □ Add regex pattern examples for phone
  □ Add json_schema_extra examples to classes
  □ Add validation rule comments
  □ Document error responses
  □ Check Swagger UI looks good (/docs)

Learning Goals:
  - Understand OpenAPI/Swagger documentation
  - See how Field() descriptions show in API docs
  - Document APIs for users

Code Pattern:
  from pydantic import Field
  
  class UserRegisterRequest(BaseModel):
      email: EmailStr = Field(
          ..., 
          description="User email (must be valid)",
          example="john@example.com"
      )
      password: str = Field(
          ...,
          min_length=8,
          description="Strong password (8+ chars, uppercase, digit, special)",
          example="SecurePass123!"
      )
      phone: Optional[str] = Field(
          None,
          description="Optional phone (+1234567890 or 123-456-7890)",
          example="+1234567890"
      )

Run After:
  Start the server: uvicorn app.main:app --reload
  Visit: http://localhost:8000/docs
  Test each endpoint, see documentation


FINAL TASK: Run All Phase 1 Tests
- Duration: 10 minutes
- Command:
  pytest tests/test_auth_basics.py -v --cov=app.schemas
  
- Should Pass:
  ✓ test_register_success
  ✓ test_register_duplicate_email
  ✓ test_register_invalid_email
  ✓ test_register_weak_password
  ✓ test_register_missing_required_field
  ✓ test_password_validation (all parametrized cases)
  ✓ test_invalid_emails (all parametrized cases)
  ✓ All unit tests for password hashing
  ✓ All unit tests for token generation
"""

# ============================================================================
# DEPENDENCIES & BLOCKERS
# ============================================================================

"""
Before Starting Phase 1:
✓ Pytest installed (already done)
✓ conftest.py created (already done)
✓ test_auth_basics.py created (already done)

Phase 1 Depends On:
✓ Current auth.py endpoint working (GET /auth/register, POST /auth/login)
  If not: Fix endpoints first

Phase 1 Enables Phase 2:
✓ Cannot write good tests without good schemas
✓ Cannot implement error handling without error schemas
✓ Phase 2 builds directly on Phase 1 work
"""

# ============================================================================
# SUCCESS CRITERIA FOR PHASE 1
# ============================================================================

"""
✓ Password validation rejects weak passwords
✓ Email validation rejects invalid formats
✓ Phone validation accepts multiple formats
✓ All validation errors have clear messages
✓ Swagger UI (/docs) shows all validation rules
✓ All test_auth_basics.py tests pass
✓ Code coverage > 90% for schemas
✓ No security warnings for password handling
"""

# ============================================================================
# RESOURCES & REFERENCES
# ============================================================================

"""
Learning Resources:

1. Pydantic Validation:
   https://docs.pydantic.dev/latest/concepts/validators/

2. Field Validators:
   https://docs.pydantic.dev/latest/api/functional_validators/#field-validator

3. Regex Testing:
   https://regex101.com/ (test regex patterns here)

4. FastAPI Validation:
   https://fastapi.tiangolo.com/tutorial/request-body/

5. Our test examples:
   tests/test_auth_basics.py (see all test cases)

6. Our pytest guide:
   tests/PYTEST_BASICS_GUIDE.md (see pytest fundamentals)

Key Files to Read:
- backend/app/schemas/auth.py (current schemas)
- backend/app/core/security.py (password hashing)
- tests/conftest.py (fixtures)
- tests/test_auth_basics.py (working test examples)
"""

# ============================================================================
# QUICK START COMMAND
# ============================================================================

"""
START HERE:

1. Read this document (you are here!)

2. Run existing tests:
   cd backend
   pytest tests/test_auth_basics.py -v

3. You'll see some tests fail (expected)

4. Follow TASK 1.1-1.5 in order

5. Run tests after each task:
   pytest tests/test_auth_basics.py -v

6. When all tests pass, move to Phase 2

Current Estimated Timeline:
- Task 1.1: 20 min
- Task 1.2: 30 min
- Task 1.3: 25 min
- Task 1.4: 20 min
- Task 1.5: 25 min
- Final Test: 10 min
TOTAL: ~2.5 hours
"""

print("✓ Phase 1 Detailed TODOs Ready!")
print("✓ Run: pytest tests/test_auth_basics.py -v")
print("✓ Follow TASK 1.1-1.5 in order")