"""
Database configuration module.
Manages dual database connections: SQLite (local/offline) and MySQL (remote/online).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
import sys
from dotenv import load_dotenv
import sys
import json
import time

# Load environment variables
load_dotenv()

# Determine database path based on environment
def get_database_path():
    """Get the appropriate database path for the current environment"""
    # Check if running as PyInstaller executable
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use APPDATA
        appdata_dir = os.path.join(os.getenv('APPDATA'), 'PharmaGestion')
        os.makedirs(appdata_dir, exist_ok=True)
        db_path = os.path.join(appdata_dir, 'pharmacy_local.db')
        print(f"[DEBUG] Using APPDATA database: {db_path}")
        return f"sqlite:///{db_path}"
    else:
        # Running in development - use local directory
        return "sqlite:///./pharmacy_local.db"

# Database URLs from environment
DATABASE_URL_LOCAL = os.getenv("DB_URL_LOCAL", get_database_path())
DATABASE_URL_REMOTE = os.getenv("DB_URL_REMOTE", "mysql+pymysql://root:@localhost:3306/pharmacy_db")

# Create engines
# SQLite engine (local/offline)
engine_local = create_engine(
    DATABASE_URL_LOCAL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL_LOCAL else {},
    echo=False  # Set to True for SQL query logging
)

# MySQL engine (remote/online)
engine_remote = create_engine(
    DATABASE_URL_REMOTE,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False
)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_local)
SessionRemote = sessionmaker(autocommit=False, autoflush=False, bind=engine_remote)

# Create declarative base
Base = declarative_base()


# Dependency injection for FastAPI
def get_local_db() -> Generator:
    """
    Dependency to get local database session (SQLite).
    Used for offline operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_remote_db() -> Generator:
    """
    Dependency to get remote database session (MySQL).
    Used for online operations and synchronization.
    """
    db = SessionRemote()
    try:
        yield db
    finally:
        db.close()


def init_local_db():
    """
    Initialize local SQLite database.
    Creates all tables defined in models.
    """
    # #region agent log
    try:
        with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"id": "log_db_init_start", "timestamp": int(time.time() * 1000), "location": "database/core.py:86", "message": "Database initialization started", "data": {"db_path": DATABASE_URL_LOCAL}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
    except: pass
    # #endregion
    # Import all models to ensure they are registered with Base
    # #region agent log
    try:
        with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"id": "log_models_import_start", "timestamp": int(time.time() * 1000), "location": "database/core.py:94", "message": "Starting models import", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
    except: pass
    # #endregion
    from app.models import (
        User, Medicine, MedicineFamily, MedicineType,
        Supplier, Customer, Sale, SaleItem,
        RestockOrder, RestockItem, Settings, SyncLog
    )
    # #region agent log
    try:
        with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"id": "log_models_import_success", "timestamp": int(time.time() * 1000), "location": "database/core.py:99", "message": "Models imported successfully", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
    except: pass
    # #endregion
    try:
        Base.metadata.create_all(bind=engine_local)
        # #region agent log
        try:
            with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"id": "log_db_create_tables_success", "timestamp": int(time.time() * 1000), "location": "database/core.py:101", "message": "Tables created successfully", "data": {}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        except: pass
        # #endregion
        print("[OK] Local database (SQLite) initialized successfully!")
    except Exception as e:
        # #region agent log
        try:
            with open(r'c:\Pharma_logiciels_version_01\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"id": "log_db_create_tables_error", "timestamp": int(time.time() * 1000), "location": "database/core.py:104", "message": "Error creating tables", "data": {"error": str(e), "type": type(e).__name__}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        except: pass
        # #endregion
        raise

    # Check if admin user exists, if not create one
    from sqlalchemy.orm import Session
    from app.models.user import User, UserRole
    from app.utils.security import hash_password
    
    session = Session(bind=engine_local)
    try:
        admin_exists = session.query(User).filter(User.username == "admin").first()
        if not admin_exists:
            print("[*] Creating default admin user...")
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role=UserRole.SUPER_ADMIN,
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            print("[OK] Default admin user created (user: admin, pass: admin123)")
    except Exception as e:
        print(f"[WARNING] Could not create default admin: {e}")
    finally:
        session.close()


def init_remote_db():
    """
    Initialize remote MySQL database.
    Creates all tables defined in models.
    Note: Database 'pharmacy_db' must exist in MySQL first.
    """
    # Import all models to ensure they are registered with Base
    from app.models import (
        User, Medicine, MedicineFamily, MedicineType,
        Supplier, Customer, Sale, SaleItem,
        RestockOrder, RestockItem, Settings, SyncLog
    )
    
    try:
        Base.metadata.create_all(bind=engine_remote)
        print("[OK] Remote database (MySQL) initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Error initializing remote database: {e}")
        print("Make sure MySQL is running and 'pharmacy_db' database exists.")


def check_database_connection(use_remote: bool = False) -> bool:
    """
    Check if database connection is available.
    
    Args:
        use_remote: If True, check remote MySQL connection. Otherwise, check local SQLite.
    
    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        engine = engine_remote if use_remote else engine_local
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
