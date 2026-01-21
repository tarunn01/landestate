# LandEstate - Property Marketplace Platform

A production-grade geospatial property marketplace platform built with FastAPI and React, connecting property owners, brokers, and buyers.

## Start

### Backend Setup

```bash
cd backend
python -m venv backvenv
source backvenv/bin/activate  # Windows: backvenv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Server will run on `http://127.0.0.1:8000`

### API Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

##  Architecture

LandEstate follows a **Layered Architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│               Frontend (React + Vite)               │
│        (App.jsx, components/, pages/, services/)    │
└────────────────┬────────────────────────────────────┘
                 │ HTTP/REST API
┌────────────────▼────────────────────────────────────┐
│          API Layer (routes.py, v1/*.py)             │
│    ├─ Auth, Properties, Users, Reviews endpoints    │
│    └─ Request validation, response serialization    │
└────────────────┬────────────────────────────────────┘
                 │ Dependency Injection
┌────────────────▼────────────────────────────────────┐
│        Business Logic Layer (services/)             │
│    ├─ Authentication logic, authorization           │
│    ├─ Property business rules                       │
│    └─ Review management                             │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│         Data Access Layer (models/, CRUD)           │
│    ├─ SQLAlchemy ORM models                         │
│    ├─ Database queries                              │
│    └─ Data transformation                           │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│      Core Layer (config, security, database)        │
│    ├─ JWT token generation & validation             │
│    ├─ Password hashing (bcrypt)                     │
│    └─ Database connection pool                      │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│   PostgreSQL Database with PostGIS (Geospatial)     │
│    ├─ users table (authentication)                  │
│    ├─ properties table (listings)                   │
│    ├─ locations table (geospatial data)             │
│    └─ reviews table (user feedback)                 │
└─────────────────────────────────────────────────────┘
```

### Data Flow Example: Creating a Property

```
User (Frontend) 
   │
   ├─> POST /properties with property data
   │
Client (React)
   │
   ├─> HTTP Request
   │
API Layer (routes.py)
   │
   ├─> Extract JWT token from headers
   ├─> Validate request schema (Pydantic)
   │
Business Logic (services/)
   │
   ├─> Check user authorization
   ├─> Apply business rules
   │
Data Access Layer (models/)
   │
   ├─> Create SQLAlchemy instance
   ├─> Save to database
   │
Database (PostgreSQL)
   │
   ├─> Store data
   ├─> Generate ID
   │
Response back to Client
   │
   └─> JSON: { property_id, status, data }
```

### Key Architectural Decisions

1. **Layered Architecture**: Each layer has a specific responsibility
   - Clear separation makes testing and maintenance easier
   - Easy to swap implementations (e.g., database)

2. **Dependency Injection**: FastAPI's `Depends()` provides:
   - Automatic request validation
   - Centralized authentication checks
   - Database session management

3. **Type Safety**: Pydantic schemas ensure:
   - Input validation
   - Response schema consistency
   - IDE autocomplete

4. **Resource-Based Design**: Endpoints are organized by resource:
   - `/auth` for authentication
   - `/properties` for property listings
   - `/users` for user profiles
   - `/reviews` for reviews

##  Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization & middleware
│   ├── api/                    # HTTP request handlers
│   │   ├── routes.py           # Main router (combines all endpoints)
│   │   ├── dependencies.py     # JWT & DB session dependencies
│   │   └── v1/                 # API version 1
│   │       ├── auth.py         # Login, register, token refresh
│   │       ├── properties.py   # CRUD operations for properties
│   │       ├── locations.py    # Location/geospatial endpoints
│   │       ├── reviews.py      # Property reviews
│   │       └── users.py        # User profile endpoints
│   ├── schemas/                # Pydantic models (validation & docs)
│   │   ├── auth.py             # Auth request/response schemas
│   │   ├── property.py         # Property DTOs
│   │   ├── locations.py        # Location schemas
│   │   ├── reviews.py          # Review schemas
│   │   └── common.py           # Base models, pagination
│   ├── models/                 # SQLAlchemy ORM models (database schema)
│   │   ├── user.py             # User table definition
│   │   ├── properties.py       # Property table definition
│   │   ├── locations.py        # Location table (PostGIS geospatial)
│   │   └── reviews.py          # Review table definition
│   ├── services/               # Business logic (future expansion)
│   │   └── __init__.py
│   ├── crud/                   # CRUD operations (future expansion)
│   │   └── __init__.py
│   └── core/                   # Configuration & utilities
│       ├── config.py           # Environment variables, settings
│       ├── database.py         # SQLAlchemy engine, session factory
│       └── security.py         # JWT token, password hashing logic
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata
└── init_db.py                  # Database initialization script

frontend/
├── src/
│   ├── App.jsx                 # Main React component
│   ├── main.jsx                # React entry point
│   ├── components/             # Reusable React components
│   │   ├── Header.jsx
│   │   ├── PropertyCard.jsx
│   │   └── ...
│   ├── pages/                  # Page-level components (routes)
│   │   ├── PropertyList.jsx
│   │   ├── PropertyDetail.jsx
│   │   ├── Login.jsx
│   │   └── ...
│   └── services/               # API client & utilities
│       └── api.js              # Axios/Fetch wrapper for backend
├── index.html                  # HTML entry point
├── package.json                # NPM dependencies
└── vite.config.js              # Vite build configuration
```

### Folder Responsibilities

| Folder | Purpose | Example |
|--------|---------|---------|
| `api/` | HTTP endpoints & routing | Defines `POST /auth/login` |
| `schemas/` | Input/output validation & documentation | Validates login credentials |
| `models/` | Database tables & relationships | Defines `users` table structure |
| `core/` | Security, config, database setup | JWT token generation |
| `services/` | Business logic (future expansion) | Complex operations |
| `crud/` | Database queries (future expansion) | Query builders |

##  Authentication

All protected endpoints use JWT tokens. Include in request header:

```
Authorization: Bearer <your_jwt_token>
```

### Auth Endpoints
- `POST /auth` - Register user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user
- `PATCH /auth/me` - Update user profile
- `POST /auth/refresh` - Refresh token

##  Property Endpoints

- `GET /properties` - List properties (with pagination)
- `POST /properties` - Create new property
- `GET /properties/{property_id}` - Get property details
- `PUT /properties/{property_id}` - Update property
- `DELETE /properties/{property_id}` - Delete property

##  User Endpoints

- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user profile

##  Database

**PostgreSQL with PostGIS** for geospatial queries

Tables:
- `users` - User accounts
- `properties` - Property listings
- `reviews` - Property reviews
- `locations` - Geospatial data

##  Tech Stack

- **Backend**: FastAPI 0.110.0
- **Database**: PostgreSQL + PostGIS
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT (python-jose)
- **Validation**: Pydantic v1
- **Server**: Uvicorn
- **Password**: bcrypt

##  Dependencies

```
fastapi==0.110.0
uvicorn[standard]==0.27.1
pydantic==1.10.26
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pyjwt==2.10.1
geoalchemy2==0.14.1
shapely==2.0.2
```

##  Architecture Highlights

### Pure FastAPI with Resource Classes

All endpoints follow a clean **class-based Resource pattern** using FastAPI's `Depends()` dependency injection:

```python
class Auth:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    async def login(self, request):
        # Business logic
        ...

@router.post("/login")
async def login(request, auth: Auth = Depends()):
    return await auth.login(request)
```

### Type Safety
- Full Pydantic validation
- IDE autocomplete support
- Type hints throughout

### JWT Authentication
- 15-minute access tokens
- 7-day refresh tokens
- Secure password hashing with bcrypt

##  Migration History

This project was migrated from `fastapi-restful` to pure FastAPI for better compatibility and maintainability. All 13 endpoints have been converted and are now fully functional more to be added soon.

##  Environment Variables

Create `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost/landestate 
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

##  Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

##  Deployment

The API is configured for production deployment. Set environment variables and use:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📊 API Response Format

All responses follow consistent JSON format:

```json
{
  "data": {},
  "status": "success",
  "message": "Operation successful"
}
```

Error responses:

```json
{
  "detail": "Error message"
}
```

## Contributing

1. Create feature branch
2. Make changes
3. Test endpoints via Swagger UI
4. Commit and push

##  Support

For API documentation, visit: http://127.0.0.1:8000/docs

---

**Last Updated**: January 19, 2026  
**Status**: ✅ Production Ready
