# LandEstate Frontend Onboarding Guide

## Project Overview

**LandEstate** is a geospatial property marketplace platform built with:
- **Backend**: FastAPI (Python) - REST API with JWT authentication
- **Frontend**: React + Vite (Your role)
- **Database**: PostgreSQL with PostGIS (geospatial support)
- **Architecture**: Microservices-ready with resource-based APIs

---

## Part 1: Understanding the Backend

### Tech Stack
- **Framework**: FastAPI 0.88.0
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT tokens (access + refresh)
- **Database**: PostgreSQL (localhost:5432)
- **Server**: Uvicorn

### Key Concepts

**Authentication Flow:**
1. User registers → Server returns access_token + refresh_token
2. User includes access_token in Authorization header for protected endpoints
3. Access tokens expire in 60 minutes
4. Use refresh_token to get new access_token

**API Base URL:**
```
http://localhost:8000/api/v1
```

---

## Part 2: Running the Backend Locally

### Prerequisites
- Python 3.11+
- PostgreSQL 18+
- Virtual environment

### Setup Steps

**1. Navigate to backend**
```powershell
cd d:\latest_projects\landestate\landestate\backend
```

**2. Activate virtual environment**
```powershell
.\backvenv\Scripts\Activate
```

**3. Ensure database is running**
```powershell
# Check if PostgreSQL is running
psql -U postgres -d landestate -c "SELECT 1"
```

**4. Start the server**
```powershell
python -m uvicorn app.main:app --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**5. Check API docs**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Part 3: All Available Endpoints

### Authentication Endpoints (`/auth`)

| Method | Endpoint    | Auth   | Purpose |
|--------|----------  |------  |---------|
| `POST` | `/auth` | ❌ |  Register new user |
| `POST` | `/auth/login`| ❌ | Login user |
| `GET` | `/auth/me` | ✅ | Get current user profile |
| `PATCH` | `/auth/me` | ✅ | Update user profile |
| `POST` | `/auth/logout` | ✅ | Logout user |
| `POST` | `/auth/refresh` | ❌ | Get new access token |

**Example: Register**
```
POST http://localhost:8000/api/v1/auth
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "OWNER"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "OWNER",
    "is_active": true,
    "created_at": "2026-01-13T10:00:00",
    "updated_at": "2026-01-13T10:00:00"
  }
}
```

---

### Properties Endpoints (`/properties`)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| `GET` | `/properties` | ❌ | List all properties |
| `POST` | `/properties` | ✅ | Create property |
| `GET` | `/properties/{id}` | ❌ | Get property details |
| `PUT` | `/properties/{id}` | ✅ | Update property |
| `DELETE` | `/properties/{id}` | ✅ | Delete property |

**Example: List Properties**
```
GET http://localhost:8000/api/v1/properties?skip=0&limit=10
```

**Response:**
```json
{
  "total": 5,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": "prop-uuid-1",
      "title": "Modern Apartment",
      "description": "3-bedroom apartment",
      "price": 250000,
      "city": "New York",
      "address": "123 Main St",
      "bedrooms": 3,
      "bathrooms": 2,
      "plot_size": 1500,
      "built_area": 1200,
      "broker_id": "user-uuid",
      "created_at": "2026-01-10T10:30:00",
      "updated_at": "2026-01-10T10:30:00"
    }
  ]
}
```

**Example: Create Property (requires auth)**
```
POST http://localhost:8000/api/v1/properties
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Beautiful House",
  "description": "3 bedroom house with garden",
  "price": 350000,
  "city": "New York",
  "address": "456 Oak Ave",
  "bedrooms": 3,
  "bathrooms": 2,
  "plot_size": 2000,
  "built_area": 1500
}
```

---

### Users Endpoints (`/users`)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| `GET` | `/users/{id}` | ✅ | Get user profile |
| `PUT` | `/users/{id}` | ✅ | Update user |
| `DELETE` | `/users/{id}` | ✅ | Delete user |

---

## Part 4: How to Call API from React

### Using Fetch API

```javascript
// Set up base URL
const API_BASE = "http://localhost:8000/api/v1";

// Register
async function register(email, password, firstName, lastName, phone, role) {
  const response = await fetch(`${API_BASE}/auth`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      password,
      first_name: firstName,
      last_name: lastName,
      phone,
      role
    })
  });
  
  if (!response.ok) throw new Error("Registration failed");
  return response.json(); // Contains access_token
}

// Login
async function login(email, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  
  if (!response.ok) throw new Error("Login failed");
  return response.json(); // Contains access_token
}

// Get current user (requires token)
async function getCurrentUser(accessToken) {
  const response = await fetch(`${API_BASE}/auth/me`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${accessToken}`,
      "Content-Type": "application/json"
    }
  });
  
  if (!response.ok) throw new Error("Failed to get user");
  return response.json();
}

// Get all properties (no auth needed)
async function getProperties(skip = 0, limit = 10) {
  const response = await fetch(
    `${API_BASE}/properties?skip=${skip}&limit=${limit}`
  );
  
  if (!response.ok) throw new Error("Failed to get properties");
  return response.json();
}

// Create property (requires auth)
async function createProperty(accessToken, propertyData) {
  const response = await fetch(`${API_BASE}/properties`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${accessToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(propertyData)
  });
  
  if (!response.ok) throw new Error("Failed to create property");
  return response.json();
}
```

### Using Axios (Recommended)

```javascript
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/v1"
});

// Add token to all requests
export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}

// Login
export async function login(email, password) {
  const response = await api.post("/auth/login", { email, password });
  return response.data;
}

// Get current user
export async function getCurrentUser() {
  const response = await api.get("/auth/me");
  return response.data;
}

// Get properties
export async function getProperties(skip = 0, limit = 10) {
  const response = await api.get("/properties", { 
    params: { skip, limit } 
  });
  return response.data;
}

// Create property
export async function createProperty(data) {
  const response = await api.post("/properties", data);
  return response.data;
}
```

---

## Part 5: Token Management in React

### Store Token in LocalStorage

```javascript
// Login and store token
async function handleLogin(email, password) {
  const { access_token } = await login(email, password);
  
  // Store token
  localStorage.setItem("access_token", access_token);
  
  // Set axios header
  setAuthToken(access_token);
  
  // Redirect to dashboard
  navigate("/dashboard");
}

// Logout
function handleLogout() {
  localStorage.removeItem("access_token");
  delete api.defaults.headers.common["Authorization"];
  navigate("/login");
}

// On app startup, restore token
useEffect(() => {
  const token = localStorage.getItem("access_token");
  if (token) {
    setAuthToken(token);
  }
}, []);
```

---

## Part 6: Project Structure

```
landestate/
├── backend/                    # Your reference (don't modify)
│   ├── app/
│   │   ├── api/v1/            # All endpoints here
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Request/response schemas
│   │   └── core/              # Config, security, database
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Your work area
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API calls (create api.js)
│   │   ├── App.jsx           # Main app
│   │   └── main.jsx          # Entry point
│   ├── package.json
│   └── vite.config.js
```

---

## Part 7: Frontend Setup

### 1. Install Dependencies
```powershell
cd frontend
npm install
```

### 2. Install API Client (Axios)
```powershell
npm install axios
```

### 3. Create API Service File

Create `frontend/src/services/api.js`:
```javascript
import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json"
  }
});

// Intercept requests to add token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercept responses for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired - redirect to login
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 4. Start Development Server
```powershell
npm run dev
```

**Frontend will run on:** http://localhost:5173

---

## Part 8: CORS Configuration

Backend allows requests from:
- http://localhost:3000
- http://localhost:5173 (Vite)

If you get CORS errors, contact backend maintainer to update CORS settings in `app/core/config.py`.

---

## Part 9: Important Notes for Frontend

### ✅ Do's
- Store token in localStorage after login
- Always include token in Authorization header for protected endpoints
- Handle 401 errors by redirecting to login
- Display loading states while API calls are pending
- Validate form inputs before sending to API

### ❌ Don'ts
- Don't hardcode API URLs - use environment variables
- Don't expose tokens in URL/query params
- Don't make requests without proper error handling
- Don't forget to handle network timeouts
- Don't call API multiple times for same data - use caching

### Environment Variables

Create `.env` in frontend folder:
```
VITE_API_BASE=http://localhost:8000/api/v1
VITE_APP_NAME=LandEstate
```

Use in code:
```javascript
const API_BASE = import.meta.env.VITE_API_BASE;
```

---

## Part 10: Testing the Connection

### Step 1: Start Backend
```powershell
# In backend folder
python -m uvicorn app.main:app --port 8000
```

### Step 2: Test in Browser
Open: http://localhost:8000/docs

Try:
- POST `/auth` - Register
- POST `/auth/login` - Login (copy access_token)
- Click "Authorize" button, paste: `Bearer {access_token}`
- GET `/auth/me` - Should return your user

### Step 3: Start Frontend
```powershell
cd frontend
npm run dev
```

### Step 4: Test API Call from React
Create a test component:
```javascript
import { useEffect, useState } from "react";
import api from "./services/api";

export default function ApiTest() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/properties?skip=0&limit=10")
      .then((res) => setData(res.data))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      {error && <p>Error: {error}</p>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}
```

If this works → Backend and Frontend are connected! ✅

---

## Part 11: Common Issues

### Issue: CORS Error
**Solution**: Backend CORS settings need updating. Contact backend team.

### Issue: 401 Unauthorized
**Solution**: Token is missing or expired. Re-login and get new token.

### Issue: 404 Not Found
**Solution**: Check endpoint URL spelling. Use `/api/v1` prefix.

### Issue: Network timeout
**Solution**: Ensure backend is running on port 8000.

---

## Part 12: Next Steps

1. ✅ Get backend running locally
2. ✅ Create `services/api.js` with axios setup
3. ✅ Build login/register pages
4. ✅ Build property listing page
5. ✅ Build property detail page
6. ✅ Build property creation form
7. ✅ Add user profile page

---

## Questions?

- **Backend issues**: Check `backend/app/main.py` and error logs
- **API issues**: Test endpoints in Swagger UI first
- **Frontend issues**: Check browser console for errors

Good luck! 🚀
