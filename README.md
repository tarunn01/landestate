# LandEstate - Property Marketplace Platform

A production-grade geospatial property marketplace platform built with FastAPI and React, connecting property owners, brokers, and buyers.

## 🚀 Quick Start

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

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── api/
│   │   ├── routes.py          # Main router
│   │   ├── dependencies.py     # JWT dependencies
│   │   └── v1/
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── properties.py  # Property endpoints
│   │       └── users_endpoints.py  # User endpoints
│   ├── schemas/
│   │   ├── auth.py            # Auth schemas
│   │   ├── property.py        # Property schemas
│   │   └── common.py          # Common/base schemas
│   ├── models/
│   │   ├── user.py            # User model
│   │   └── properties.py      # Property model
│   └── core/
│       ├── config.py          # Configuration
│       ├── database.py        # Database setup
│       └── security.py        # JWT & password hashing
├── requirements.txt
└── .env
```

## 🔐 Authentication

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

## 🏘️ Property Endpoints

- `GET /properties` - List properties (with pagination)
- `POST /properties` - Create new property
- `GET /properties/{property_id}` - Get property details
- `PUT /properties/{property_id}` - Update property
- `DELETE /properties/{property_id}` - Delete property

## 👥 User Endpoints

- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user profile

## 🗄️ Database

**PostgreSQL with PostGIS** for geospatial queries

Tables:
- `users` - User accounts
- `properties` - Property listings
- `reviews` - Property reviews
- `locations` - Geospatial data

## 🛠️ Tech Stack

- **Backend**: FastAPI 0.110.0
- **Database**: PostgreSQL + PostGIS
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT (python-jose)
- **Validation**: Pydantic v1
- **Server**: Uvicorn
- **Password**: bcrypt

## 📦 Dependencies

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

## ✨ Architecture Highlights

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

## 🔄 Migration History

This project was migrated from `fastapi-restful` to pure FastAPI for better compatibility and maintainability. All 13 endpoints have been converted and are now fully functional.

## 📝 Environment Variables

Create `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost/landestate
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

## 🚀 Deployment

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

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test endpoints via Swagger UI
4. Commit and push

## 📞 Support

For API documentation, visit: http://127.0.0.1:8000/docs

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: January 6, 2026  
**Status**: ✅ Production Ready
