# Quick Reference: How to Design Endpoints (Pattern)

## 📝 The Pattern Every Endpoint File Follows

```python
# File: backend/app/api/v1/{feature_name}.py

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

# Import schemas for this feature
from app.schemas.{feature_name} import (
    {Feature}CreateRequest,
    {Feature}Response,
    {Feature}UpdateRequest,
)

# Database access
from app.core.database import get_db

# Auth (for protected endpoints)
from app.core.dependencies import get_current_user

# Router for this feature
router = APIRouter(
    prefix="/{features}",           # URL prefix
    tags=["{Feature}s"],             # API docs organization
)


# ============================================================================
# ENDPOINT 1: GET /{features} - LIST WITH PAGINATION
# ============================================================================

@router.get(
    "",
    response_model=PaginatedResponse[{Feature}Response],
    summary="List all {features}",
    description="Get all {features} with pagination and filtering",
)
async def list_{features}(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    ✅ What to implement:
    1. Calculate offset = (page - 1) * page_size
    2. Query database with LIMIT and OFFSET
    3. Count total items
    4. Return PaginatedResponse with items and pagination info
    
    ❌ Common mistakes:
    - Not validating page >= 1
    - Not limiting page_size to prevent huge responses
    - Not counting total for pagination
    """
    pass


# ============================================================================
# ENDPOINT 2: GET /{features}/{id} - GET SINGLE ITEM
# ============================================================================

@router.get(
    "/{id}",
    response_model={Feature}Response,
    summary="Get {feature} details",
)
async def get_{feature}(
    id: str,  # Will be in URL: /properties/123
    db: Session = Depends(get_db),
):
    """
    ✅ What to implement:
    1. Query database by id
    2. If not found, raise HTTPException(404)
    3. Return the item
    
    ❌ Common mistakes:
    - Not checking if item exists (returns None)
    - Not raising 404 error
    - Not checking permissions (if needed)
    """
    pass


# ============================================================================
# ENDPOINT 3: POST /{features} - CREATE NEW ITEM
# ============================================================================

@router.post(
    "",
    response_model={Feature}Response,
    status_code=status.HTTP_201_CREATED,  # 201 = Created
    summary="Create new {feature}",
)
async def create_{feature}(
    request: {Feature}CreateRequest,  # Request body validation
    current_user=Depends(get_current_user),  # Requires login
    db: Session = Depends(get_db),
):
    """
    ✅ What to implement:
    1. Validate request data (Pydantic does this auto)
    2. Check permissions (user can create)
    3. Check for duplicates if needed
    4. Create database record
    5. Return created item with 201 status
    
    ❌ Common mistakes:
    - Not checking permissions
    - Not validating required fields
    - Not checking duplicates (email, username, etc)
    - Returning 200 instead of 201
    """
    pass


# ============================================================================
# ENDPOINT 4: PUT /{features}/{id} - FULL UPDATE
# ============================================================================

@router.put(
    "/{id}",
    response_model={Feature}Response,
    summary="Update {feature}",
)
async def update_{feature}(
    id: str,
    request: {Feature}UpdateRequest,  # All fields optional for update
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ What to implement:
    1. Find item by id
    2. Check if exists (404 if not)
    3. Check permissions (user owns it)
    4. Update only fields that were sent
    5. Save to database
    6. Return updated item
    
    ❌ Common mistakes:
    - Not checking if item exists
    - Not checking permissions
    - Updating fields not in request (should be null/None)
    - Not validating new data
    """
    pass


# ============================================================================
# ENDPOINT 5: DELETE /{features}/{id} - DELETE ITEM
# ============================================================================

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,  # 204 = No Content
    summary="Delete {feature}",
)
async def delete_{feature}(
    id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ What to implement:
    1. Find item by id
    2. Check if exists (404 if not)
    3. Check permissions (user owns it)
    4. Delete from database
    5. Return 204 (no content)
    
    ❌ Common mistakes:
    - Not checking if item exists
    - Not checking permissions
    - Returning data instead of 204
    - Not checking for dependent records
    """
    pass
```

---

## 🔍 Request/Response Examples

### Example 1: Create Property

**REQUEST (POST /api/v1/properties)**
```json
{
  "title": "2 Acre Land",
  "description": "Beautiful land with road access",
  "property_type": "RESIDENTIAL",
  "price": 500000,
  "currency": "USD",
  "area_sqft": 87120,
  "location_id": "loc-123",
  "amenities": ["Road Access", "Water"],
  "contact_phone": "+1234567890",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[40.7128, -74.0060], [40.7130, -74.0060], ...]]
  }
}
```

**RESPONSE (201 Created)**
```json
{
  "id": "prop-789",
  "title": "2 Acre Land",
  "description": "Beautiful land with road access",
  "property_type": "RESIDENTIAL",
  "price": 500000,
  "currency": "USD",
  "area_sqft": 87120,
  "total_area_sqm": 8090,
  "location": {
    "id": "loc-123",
    "name": "Downtown Area",
    ...
  },
  "broker": {
    "id": "broker-1",
    "name": "John Smith",
    ...
  },
  "amenities": ["Road Access", "Water"],
  "images": [],
  "reviews": [],
  "status": "AVAILABLE",
  "views_count": 0,
  "favorites_count": 0,
  "geometry": {...},
  "created_at": "2024-01-03T10:30:00Z",
  "updated_at": "2024-01-03T10:30:00Z"
}
```

---

## 🛡️ Error Handling Pattern

```python
from fastapi import HTTPException, status

# Item not found
if not item:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Item not found",
    )

# Unauthorized (not logged in)
if not current_user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )

# Forbidden (logged in but can't access)
if item.user_id != current_user.id:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access this resource",
    )

# Bad request (invalid input)
if request.price < 0:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Price must be positive",
    )
```

---

## 🎯 Status Codes You'll Use

| Code | When to Use | Example |
|------|------------|---------|
| 200 | GET, PUT success | `GET /properties/123` |
| 201 | POST success | `POST /properties` creates item |
| 204 | DELETE success | `DELETE /properties/123` |
| 400 | Invalid input | Price is negative, email invalid |
| 401 | Not authenticated | No JWT token provided |
| 403 | Not authorized | Token valid but user can't access |
| 404 | Not found | `GET /properties/invalid-id` |
| 429 | Rate limited | Too many requests |
| 500 | Server error | Exception during processing |

---

## 📦 Pagination Pattern

**Request:**
```
GET /properties?page=1&page_size=20
```

**Response:**
```json
{
  "total": 250,           // Total items in database
  "page": 1,              // Current page
  "page_size": 20,        // Items returned
  "total_pages": 13,      // Total pages (250 / 20)
  "items": [...]          // The actual items
}
```

**Implementation:**
```python
skip = (page - 1) * page_size
limit = page_size

# Query
items = db.query(Model).offset(skip).limit(limit).all()
total = db.query(Model).count()
total_pages = (total + page_size - 1) // page_size

return PaginatedResponse(
    total=total,
    page=page,
    page_size=page_size,
    total_pages=total_pages,
    items=items,
)
```

---

## 🔐 Permission Pattern

```python
async def require_owner(
    id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if current user owns the resource."""
    item = db.query(Property).filter(Property.id == id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return item

# Usage
@router.put("/{id}")
async def update_property(
    request: PropertyUpdateRequest,
    property_=Depends(require_owner),  # Auto-checked
):
    # Safe to update - ownership already verified
    pass
```

---

## ✨ Tips for Interview

When showing your code:

1. **Point out the pattern:**
   "I follow REST conventions - GET for read, POST for create, PUT for update, DELETE for delete"

2. **Explain error handling:**
   "I always check if item exists and raise 404. I verify permissions before allowing updates"

3. **Show validation:**
   "I use Pydantic schemas to validate all inputs automatically"

4. **Mention pagination:**
   "For list endpoints, I implement pagination to prevent loading huge datasets"

5. **Discuss status codes:**
   "I return proper status codes - 201 for creation, 204 for deletion, 404 for not found"

This shows production-level thinking!

