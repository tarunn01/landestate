# Database Schema & Models

## 📊 Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────┐
│                          Users                                   │
├─────────────────────────────────────────────────────────────────┤
│ PK  id (UUID)                                                   │
│     email (UNIQUE)                                              │
│     password_hash                                               │
│     first_name                                                  │
│     last_name                                                   │
│     phone                                                       │
│     role (USER, BROKER, OWNER, ADMIN)                          │
│     profile_picture (S3 URL)                                    │
│     is_active                                                   │
│     created_at                                                  │
│     updated_at                                                  │
└─────────────────────────────────────────────────────────────────┘
            │                                              
            │ (1:Many)                                    
            └────────────────────────────────────────────┐
                                                          │
┌─────────────────────────────────────────────────────────────────┐
│                        Brokers                                   │
├─────────────────────────────────────────────────────────────────┤
│ PK  id (UUID)                                                   │
│ FK  user_id → Users(id)                                         │
│     company_name                                                │
│     bio                                                         │
│     verified (boolean)                                          │
│     rating (0-5)                                                │
│     created_at                                                  │
│     updated_at                                                  │
└─────────────────────────────────────────────────────────────────┘
            │                                              
            │ (1:Many)                                    
            └────────────────────────────────────────────┐
                                                          │
┌─────────────────────────────────────────────────────────────────┐
│                      Locations                                   │
├─────────────────────────────────────────────────────────────────┤
│ PK  id (UUID)                                                   │
│     name                                                        │
│     address                                                     │
│     city                                                        │
│     state                                                       │
│     country                                                     │
│     zip_code                                                    │
│     latitude (float)                                            │
│     longitude (float)                                           │
│     center_point (POINT - PostGIS)  ← Geospatial               │
│     created_at                                                  │
└─────────────────────────────────────────────────────────────────┘
            │                                              
            │ (1:Many)                                    
            └────────────────────────────────────────────┐
                                                          │
┌──────────────────────────────────────────────────────────────────┐
│                      Properties                                   │
├──────────────────────────────────────────────────────────────────┤
│ PK  id (UUID)                                                    │
│ FK  broker_id → Brokers(id)                                      │
│ FK  location_id → Locations(id)                                  │
│     title                                                        │
│     description                                                  │
│     property_type (RESIDENTIAL, COMMERCIAL, etc)                │
│     price (float)                                                │
│     currency                                                     │
│     area_sqft                                                    │
│     latitude (float)                                             │
│     longitude (float)                                            │
│     geometry (POLYGON - PostGIS)  ← Plot boundaries             │
│     status (AVAILABLE, SOLD, PENDING)                           │
│     amenities (JSON array)                                       │
│     views_count                                                  │
│     favorites_count                                              │
│     contact_phone                                                │
│     created_at                                                   │
│     updated_at                                                   │
└──────────────────────────────────────────────────────────────────┘
            │                                              
    ┌───────┴───────┐                                     
    │               │                                     
    │ (1:Many)      │ (1:Many)                            
    │               │                                     
┌───▼────────┐  ┌──▼──────────────────────────────┐
│   Reviews  │  │    PropertyImages                │
├────────────┤  ├──────────────────────────────────┤
│ PK id      │  │ PK id (UUID)                     │
│ FK prop_id │  │ FK property_id → Properties(id)  │
│ FK user_id │  │    url (S3)                      │
│    rating  │  │    is_primary                    │
│    comment │  │    uploaded_at                   │
│    created │  │    created_at                    │
└────────────┘  └──────────────────────────────────┘

FK  user_id → Users(id)
    rating (1-5)
    title
    comment
    would_recommend
    created_at
    updated_at
```

---

## 🗄️ Detailed Column Definitions

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'USER',  -- USER, BROKER, OWNER, ADMIN
    profile_picture VARCHAR(500),  -- S3 URL
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Brokers Table
```sql
CREATE TABLE brokers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,  -- One broker per user
    company_name VARCHAR(255),
    bio TEXT,
    verified BOOLEAN DEFAULT FALSE,
    rating FLOAT DEFAULT 0,  -- 0-5 stars
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_brokers_user_id ON brokers(user_id);
```

### Locations Table
```sql
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    
    -- PostGIS: Point geometry for location
    center_point GEOMETRY(Point, 4326),  -- WGS84 coordinates
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locations_center_point ON locations USING GIST(center_point);
CREATE INDEX idx_locations_city ON locations(city);
```

### Properties Table
```sql
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    broker_id UUID NOT NULL,
    location_id UUID NOT NULL,
    
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    property_type VARCHAR(50) NOT NULL,  -- RESIDENTIAL, COMMERCIAL, etc
    price DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    area_sqft FLOAT NOT NULL,
    
    -- Location coordinates
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    
    -- PostGIS: Polygon geometry for plot boundary
    geometry GEOMETRY(Polygon, 4326),  -- Plot shape
    
    status VARCHAR(20) DEFAULT 'AVAILABLE',  -- AVAILABLE, SOLD, PENDING
    amenities JSONB,  -- JSON array: ["Water", "Road", "Electricity"]
    
    views_count INTEGER DEFAULT 0,
    favorites_count INTEGER DEFAULT 0,
    
    contact_phone VARCHAR(20) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (broker_id) REFERENCES brokers(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_properties_broker_id ON properties(broker_id);
CREATE INDEX idx_properties_location_id ON properties(location_id);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_price ON properties(price);

-- PostGIS indexes
CREATE INDEX idx_properties_geometry ON properties USING GIST(geometry);
CREATE INDEX idx_properties_point ON properties USING GIST(
    ST_POINT(longitude, latitude)::GEOMETRY
);
```

### PropertyImages Table
```sql
CREATE TABLE property_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL,
    
    url VARCHAR(500) NOT NULL,  -- S3 URL
    is_primary BOOLEAN DEFAULT FALSE,  -- Main image
    
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

CREATE INDEX idx_property_images_property_id ON property_images(property_id);
```

### Reviews Table
```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    comment TEXT,
    would_recommend BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_reviews_property_id ON reviews(property_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
```

---

## 🌍 PostGIS (Geospatial) Queries Examples

### Get properties within 5km radius
```sql
SELECT *
FROM properties
WHERE ST_DWithin(
    geometry,
    ST_SetSRID(ST_Point(-74.0060, 40.7128), 4326),
    5000  -- 5km in meters
)
ORDER BY ST_Distance(
    geometry,
    ST_SetSRID(ST_Point(-74.0060, 40.7128), 4326)
);
```

### Calculate distance from property to user location
```sql
SELECT 
    id,
    title,
    ST_DistanceSphere(
        geometry,
        ST_SetSRID(ST_Point(-74.0060, 40.7128), 4326)
    ) / 1000 AS distance_km
FROM properties
ORDER BY distance_km;
```

### Check if point is inside property polygon
```sql
SELECT *
FROM properties
WHERE ST_Contains(
    geometry,
    ST_SetSRID(ST_Point(-74.0065, 40.7125), 4326)
);
```

---

## 🔧 SQLAlchemy Model Example

```python
# File: backend/app/models/property.py

from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Float, Integer, ForeignKey, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Property(Base, TimestampMixin):
    __tablename__ = "properties"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    broker_id = Column(String, ForeignKey("brokers.id"), nullable=False)
    location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=False)
    property_type = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    area_sqft = Column(Float, nullable=False)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # PostGIS: Polygon for plot boundary
    geometry = Column(Geometry(geometry_type="POLYGON", srid=4326))
    
    status = Column(String(20), default="AVAILABLE")
    amenities = Column(JSONB, default=list)
    
    views_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)
    
    contact_phone = Column(String(20), nullable=False)
    
    # Relationships
    broker = relationship("Broker", back_populates="properties")
    location = relationship("Location", back_populates="properties")
    images = relationship("PropertyImage", back_populates="property")
    reviews = relationship("Review", back_populates="property")
```

---

## 🎯 Key Geospatial Concepts

| Concept | Use Case | Example |
|---------|----------|---------|
| **Point** | Single location | Property coordinates (lat, lng) |
| **Polygon** | Area/boundary | Plot shape, city boundaries |
| **LineString** | Routes | Road, boundary lines |
| **ST_Contains** | Is point inside polygon? | Is user in property area? |
| **ST_DWithin** | Distance search | Find properties within 5km |
| **ST_Distance** | Calculate distance | How far is this property? |
| **ST_Buffer** | Create radius around point | 10km buffer around location |
| **SRID 4326** | Coordinate system | WGS84 (GPS coordinates) |

---

## 📋 Migration Strategy (Alembic)

```bash
# Initialize Alembic
alembic init migrations

# Create migration from models
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# See migration history
alembic current
alembic history
```

