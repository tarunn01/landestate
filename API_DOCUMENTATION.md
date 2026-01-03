# LandEstate API Documentation

**Base URL:** `http://localhost:8000/api`  
**Version:** v1  
**Authentication:** JWT Bearer Token

---

## 📋 API Endpoints Overview

### **1. Authentication Endpoints** (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user profile

### **2. User Endpoints** (`/users`)
- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user profile
- `GET /users/{user_id}/properties` - Get user's saved properties
- `POST /users/{user_id}/favorites` - Add property to favorites
- `DELETE /users/{user_id}/favorites/{property_id}` - Remove from favorites

### **3. Property Endpoints** (`/properties`)
- `GET /properties` - List all properties (with filtering, pagination)
- `GET /properties/{property_id}` - Get property details
- `POST /properties` - Create new property (Broker/Owner only)
- `PUT /properties/{property_id}` - Update property
- `DELETE /properties/{property_id}` - Delete property
- `GET /properties/search/nearby` - Search properties by location & radius
- `GET /properties/{property_id}/images` - Get property images
- `POST /properties/{property_id}/images` - Upload property images

### **4. Broker Endpoints** (`/brokers`)
- `GET /brokers` - List all brokers
- `GET /brokers/{broker_id}` - Get broker profile
- `POST /brokers` - Register as broker
- `PUT /brokers/{broker_id}` - Update broker profile
- `GET /brokers/{broker_id}/properties` - Get broker's properties
- `GET /brokers/{broker_id}/reviews` - Get broker reviews

### **5. Location Endpoints** (`/locations`)
- `GET /locations` - List popular locations
- `GET /locations/{location_id}` - Get location details
- `GET /locations/{location_id}/properties` - Properties in location
- `GET /locations/nearby` - Get nearby locations

### **6. Review & Rating Endpoints** (`/reviews`)
- `GET /properties/{property_id}/reviews` - Get property reviews
- `POST /properties/{property_id}/reviews` - Create review
- `PUT /reviews/{review_id}` - Update review
- `DELETE /reviews/{review_id}` - Delete review

---

## 🔐 Authentication Endpoints

### **1. POST /auth/register**
Register a new user

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "USER"  // USER, BROKER, OWNER, ADMIN
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-123",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "USER",
  "created_at": "2024-01-03T10:30:00Z",
  "is_active": true
}
```

**Error (400 Bad Request):**
```json
{
  "detail": "Email already exists",
  "error_code": "EMAIL_ALREADY_EXISTS"
}
```

---

### **2. POST /auth/login**
Login user and get JWT tokens

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-123",
    "email": "user@example.com",
    "first_name": "John",
    "role": "USER"
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password",
  "error_code": "INVALID_CREDENTIALS"
}
```

---

## 🏘️ Property Endpoints

### **1. GET /properties**
List all properties with filtering, sorting, pagination

**Query Parameters:**
```
GET /properties?
  page=1&
  page_size=20&
  sort_by=created_at&
  order=desc&
  min_price=100000&
  max_price=5000000&
  property_type=RESIDENTIAL&
  status=AVAILABLE&
  location_id=uuid-456
```

**Response (200 OK):**
```json
{
  "total": 250,
  "page": 1,
  "page_size": 20,
  "total_pages": 13,
  "items": [
    {
      "id": "uuid-789",
      "title": "2 Acre Residential Plot",
      "description": "Beautiful residential land in prime location",
      "property_type": "RESIDENTIAL",
      "price": 500000,
      "currency": "USD",
      "area_sqft": 87120,
      "location": {
        "id": "uuid-456",
        "name": "Downtown Area",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "city": "New York",
        "state": "NY"
      },
      "broker": {
        "id": "uuid-broker-1",
        "name": "John Smith",
        "phone": "+1234567890",
        "email": "broker@example.com"
      },
      "image_url": "https://s3.example.com/property-1.jpg",
      "status": "AVAILABLE",
      "created_at": "2024-01-01T10:00:00Z"
    }
    // More properties...
  ]
}
```

---

### **2. GET /properties/{property_id}**
Get detailed property information

**Response (200 OK):**
```json
{
  "id": "uuid-789",
  "title": "2 Acre Residential Plot",
  "description": "Beautiful residential land in prime location",
  "property_type": "RESIDENTIAL",
  "price": 500000,
  "currency": "USD",
  "area_sqft": 87120,
  "total_area_sqm": 8090,
  "location": {
    "id": "uuid-456",
    "name": "Downtown Area",
    "address": "123 Main St",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "city": "New York",
    "state": "NY",
    "zip_code": "10001"
  },
  "broker": {
    "id": "uuid-broker-1",
    "name": "John Smith",
    "phone": "+1234567890",
    "email": "broker@example.com",
    "company": "Real Estate Co"
  },
  "amenities": ["Water Access", "Road Access", "Electricity"],
  "images": [
    {
      "id": "img-1",
      "url": "https://s3.example.com/property-1.jpg",
      "is_primary": true
    }
  ],
  "reviews": [
    {
      "id": "review-1",
      "user": "User Name",
      "rating": 5,
      "comment": "Great location!",
      "created_at": "2024-01-02T10:00:00Z"
    }
  ],
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[40.7128, -74.0060], [40.7130, -74.0060], [40.7130, -74.0058], [40.7128, -74.0058]]]
  },
  "status": "AVAILABLE",
  "views_count": 1250,
  "favorites_count": 45,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-03T10:00:00Z"
}
```

---

### **3. POST /properties**
Create new property (Broker/Owner only)

**Request Body:**
```json
{
  "title": "2 Acre Residential Plot",
  "description": "Beautiful residential land in prime location",
  "property_type": "RESIDENTIAL",
  "price": 500000,
  "currency": "USD",
  "area_sqft": 87120,
  "location_id": "uuid-456",
  "amenities": ["Water Access", "Road Access"],
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[40.7128, -74.0060], [40.7130, -74.0060], [40.7130, -74.0058], [40.7128, -74.0058]]]
  },
  "contact_phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-789",
  "title": "2 Acre Residential Plot",
  "price": 500000,
  "status": "AVAILABLE",
  "created_at": "2024-01-03T10:30:00Z"
}
```

---

### **4. GET /properties/search/nearby**
Search properties by user location (GEOSPATIAL QUERY)

**Query Parameters:**
```
GET /properties/search/nearby?
  latitude=40.7128&
  longitude=-74.0060&
  radius_km=5&
  page=1&
  page_size=20
```

**Response (200 OK):**
```json
{
  "user_location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "search_radius_km": 5,
  "total": 15,
  "items": [
    {
      "id": "uuid-789",
      "title": "2 Acre Residential Plot",
      "price": 500000,
      "distance_km": 2.5,
      "location": {
        "latitude": 40.7200,
        "longitude": -74.0120,
        "city": "New York"
      },
      "image_url": "https://s3.example.com/property-1.jpg"
    }
    // More properties sorted by distance...
  ]
}
```

---

## 👥 User Endpoints

### **1. GET /users/{user_id}**
Get user profile

**Response (200 OK):**
```json
{
  "id": "uuid-123",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "USER",
  "profile_picture": "https://s3.example.com/user-1.jpg",
  "bio": "Real estate enthusiast",
  "saved_properties_count": 5,
  "created_at": "2024-01-03T10:30:00Z"
}
```

---

### **2. POST /users/{user_id}/favorites**
Add property to favorites

**Request Body:**
```json
{
  "property_id": "uuid-789"
}
```

**Response (201 Created):**
```json
{
  "message": "Property added to favorites",
  "favorite_id": "fav-123"
}
```

---

## 📍 Location Endpoints

### **1. GET /locations**
List all locations

**Query Parameters:**
```
GET /locations?page=1&page_size=50&search=New York
```

**Response (200 OK):**
```json
{
  "total": 150,
  "page": 1,
  "items": [
    {
      "id": "uuid-456",
      "name": "Downtown Area",
      "city": "New York",
      "state": "NY",
      "country": "USA",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "property_count": 45,
      "center_point": {
        "type": "Point",
        "coordinates": [40.7128, -74.0060]
      }
    }
  ]
}
```

---

## ⭐ Review Endpoints

### **1. POST /properties/{property_id}/reviews**
Create property review

**Request Body:**
```json
{
  "rating": 4,
  "title": "Great property",
  "comment": "Well-maintained land with good access",
  "would_recommend": true
}
```

**Response (201 Created):**
```json
{
  "id": "review-1",
  "property_id": "uuid-789",
  "user_id": "uuid-123",
  "rating": 4,
  "title": "Great property",
  "comment": "Well-maintained land with good access",
  "created_at": "2024-01-03T10:30:00Z"
}
```

---

## 🔧 Error Responses

All errors follow this format:

**400 Bad Request:**
```json
{
  "detail": "Validation error message",
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated",
  "error_code": "NOT_AUTHENTICATED"
}
```

**403 Forbidden:**
```json
{
  "detail": "Not authorized",
  "error_code": "NOT_AUTHORIZED"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found",
  "error_code": "NOT_FOUND"
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_SERVER_ERROR"
}
```

---

## 📊 Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Not authorized |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

---

## 🗂️ File Structure for Implementation

```
backend/app/
├── api/
│   ├── routes.py                    ← Import all routers here
│   ├── v1/
│   │   ├── auth.py                 ← Auth endpoints
│   │   ├── users.py                ← User endpoints
│   │   ├── properties.py           ← Property endpoints
│   │   ├── brokers.py              ← Broker endpoints
│   │   ├── locations.py            ← Location endpoints
│   │   └── reviews.py              ← Review endpoints
│   └── dependencies.py             ← Shared dependencies (auth, pagination)
│
├── schemas/
│   ├── auth.py                     ← Auth request/response schemas
│   ├── user.py                     ← User schemas
│   ├── property.py                 ← Property schemas
│   ├── location.py                 ← Location schemas
│   ├── review.py                   ← Review schemas
│   └── common.py                   ← Shared schemas (error, pagination)
│
├── models/
│   ├── user.py                     ← User SQLAlchemy model
│   ├── property.py                 ← Property model
│   ├── location.py                 ← Location model
│   ├── review.py                   ← Review model
│   ├── broker.py                   ← Broker model
│   └── __init__.py                 ← Export all models
│
└── ...
```

