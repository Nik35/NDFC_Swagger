### Directory Structure

```
ndfc-sot/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── fabrics.py
│   └── services/
│       ├── __init__.py
│       └── fabric_service.py
│
├── requirements.txt
├── alembic.ini
├── migrations/
│   └── versions/
│
└── README.md
```

### Step 1: Setting Up the Environment

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install FastAPI and other dependencies**:
   Create a `requirements.txt` file with the following content:
   ```plaintext
   fastapi
   uvicorn
   sqlalchemy
   databases
   alembic
   pydantic
   python-dotenv
   ```

   Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Database Configuration

Create a `database.py` file to handle database connections using SQLAlchemy.

```python
# app/database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./ndfc_sot.db"  # Change to your database URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()
```

### Step 3: Define Models

Create a `models.py` file to define the database models.

```python
# app/models.py
from sqlalchemy import Column, Integer, String
from .database import Base

class Fabric(Base):
    __tablename__ = "fabrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    vxlan_id = Column(Integer)
```

### Step 4: Create Pydantic Schemas

Create a `schemas.py` file for request and response validation.

```python
# app/schemas.py
from pydantic import BaseModel

class FabricBase(BaseModel):
    name: str
    description: str
    vxlan_id: int

class FabricCreate(FabricBase):
    pass

class Fabric(FabricBase):
    id: int

    class Config:
        orm_mode = True
```

### Step 5: Create Services

Create a `fabric_service.py` file to handle business logic.

```python
# app/services/fabric_service.py
from sqlalchemy.orm import Session
from ..models import Fabric
from ..schemas import FabricCreate

def create_fabric(db: Session, fabric: FabricCreate):
    db_fabric = Fabric(**fabric.dict())
    db.add(db_fabric)
    db.commit()
    db.refresh(db_fabric)
    return db_fabric

def get_fabric(db: Session, fabric_id: int):
    return db.query(Fabric).filter(Fabric.id == fabric_id).first()

def get_fabrics(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Fabric).offset(skip).limit(limit).all()
```

### Step 6: Create Routers

Create a `fabrics.py` file for the API endpoints.

```python
# app/routers/fabrics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, services
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/fabrics/", response_model=schemas.Fabric)
def create_fabric(fabric: schemas.FabricCreate, db: Session = Depends(get_db)):
    return services.create_fabric(db=db, fabric=fabric)

@router.get("/fabrics/{fabric_id}", response_model=schemas.Fabric)
def read_fabric(fabric_id: int, db: Session = Depends(get_db)):
    db_fabric = services.get_fabric(db=db, fabric_id=fabric_id)
    if db_fabric is None:
        raise HTTPException(status_code=404, detail="Fabric not found")
    return db_fabric

@router.get("/fabrics/", response_model=list[schemas.Fabric])
def read_fabrics(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    fabrics = services.get_fabrics(db=db, skip=skip, limit=limit)
    return fabrics
```

### Step 7: Main Application

Create the main application file.

```python
# app/main.py
from fastapi import FastAPI
from .routers import fabrics
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(fabrics.router, prefix="/api/v1")
```

### Step 8: Run the Application

Run the FastAPI application using Uvicorn.

```bash
uvicorn app.main:app --reload
```

### Step 9: Database Migration

Set up Alembic for database migrations. Initialize Alembic and create a migration script.

```bash
alembic init migrations
```

Edit `alembic.ini` to set the database URL, and create a migration script:

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Step 10: Documentation

Create a `README.md` file to document the application, including setup instructions, API endpoints, and usage examples.

### Conclusion

This is a basic structure for a FastAPI application serving as a Source of Truth for Cisco NDFC VXLAN EVPN fabrics. You can expand upon this by adding authentication, more complex business logic, error handling, logging, and testing as needed for a production-grade application.