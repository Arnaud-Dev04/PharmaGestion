"""
Database configuration module.
Manages dual database connections: SQLite (local/offline) and MySQL (remote/online).
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
import os
import sys
from dotenv import load_dotenv

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

# MySQL engine (remote/online) — or SQLite fallback on Vercel
if "sqlite" in DATABASE_URL_REMOTE:
    engine_remote = create_engine(
        DATABASE_URL_REMOTE,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
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
class Base(DeclarativeBase):
    pass


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
    # Import all models to ensure they are registered with Base
    from app.models import (
        User, Medicine, MedicineFamily, MedicineType,
        Supplier, Customer, Sale, SaleItem,
        RestockOrder, RestockItem, Settings, SyncLog,
        Batch, POSSale, POSSaleItem, StockMovement
    )
    from app.models.medicine_pricing import MedicinePricing  # Pricing module
    try:
        Base.metadata.create_all(bind=engine_local)
        print("[OK] Local database (SQLite) initialized successfully!")
    except Exception as e:
        raise

    # Check if super admin user exists, if not create one
    from sqlalchemy.orm import Session
    from app.models.user import User, UserRole
    from app.utils.security import hash_password
    from app.models.settings import Settings
    
    session = Session(bind=engine_local)
    try:
        admin_exists = session.query(User).filter(User.username == "arnaud").first()
        if not admin_exists:
            print("[*] Creating default super admin user (arnaud)...")
            admin_user = User(
                username="arnaud",
                password_hash=hash_password("arnaud123"),
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                must_change_password=True
            )
            session.add(admin_user)
            session.commit()
            print("[OK] Default super admin user created (user: arnaud, pass: arnaud123)")
        
        # Check if is_first_setup setting exists, if not create it
        first_setup_setting = session.query(Settings).filter(Settings.key == "is_first_setup").first()
        if not first_setup_setting:
            print("[*] Setting is_first_setup flag...")
            setting = Settings(
                key="is_first_setup",
                value="true"
            )
            session.add(setting)
            session.commit()
            print("[OK] is_first_setup flag set to true")
    except Exception as e:
        print(f"[WARNING] Could not create default admin: {e}")
    finally:
        session.close()
    
    # =============================
    # AUTO-MIGRATE: Create default batches for medicines without batches
    # =============================
    session = Session(bind=engine_local)
    try:
        from app.models.batch import Batch
        from app.models.medicine import Medicine
        from datetime import date, timedelta
        
        medicines_without_batches = session.query(Medicine).filter(
            Medicine.is_active == True,
            Medicine.quantity > 0,
            ~Medicine.id.in_(
                session.query(Batch.medicine_id).distinct()
            )
        ).all()
        
        if medicines_without_batches:
            print(f"[*] Migrating {len(medicines_without_batches)} medicines to batch system...")
            for med in medicines_without_batches:
                # Create a default batch with existing stock
                default_expiry = med.expiry_date if med.expiry_date else (date.today() + timedelta(days=365))
                batch = Batch(
                    medicine_id=med.id,
                    batch_number=f"INIT-{med.code}",
                    expiration_date=default_expiry,
                    quantity=med.quantity,
                    purchase_price=med.price_buy,
                    is_active=True
                )
                session.add(batch)
            session.commit()
            print(f"[OK] {len(medicines_without_batches)} default batches created")
    except Exception as e:
        print(f"[WARNING] Batch migration skipped: {e}")
        session.rollback()
    finally:
        session.close()
    
    # =============================
    # AUTO-MIGRATE: Add customer_name column to pos_sales if missing
    # =============================
    session = Session(bind=engine_local)
    try:
        from sqlalchemy import text, inspect
        inspector = inspect(engine_local)
        if 'pos_sales' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('pos_sales')]
            if 'customer_name' not in columns:
                session.execute(text("ALTER TABLE pos_sales ADD COLUMN customer_name VARCHAR(200)"))
                session.commit()
                print("[OK] Added customer_name column to pos_sales")
    except Exception as e:
        print(f"[WARNING] pos_sales migration skipped: {e}")
        session.rollback()
    finally:
        session.close()
    
    # =============================
    # SAFETY CHECK: Report expired batches without mutating expiry dates
    # =============================
    session = Session(bind=engine_local)
    try:
        from app.models.batch import Batch
        from datetime import date
        
        expired_batches = session.query(Batch).filter(
            Batch.is_active == True,
            Batch.quantity > 0,
            Batch.expiration_date <= date.today()
        ).all()
        
        if expired_batches:
            for batch in expired_batches:
                print(
                    f"[WARNING] Batch {batch.batch_number} is expired "
                    f"({batch.expiration_date}) and will be blocked from POS sales"
                )
    except Exception as e:
        print(f"[WARNING] Batch expiry check skipped: {e}")
        session.rollback()
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
        RestockOrder, RestockItem, Settings, SyncLog,
        Batch, POSSale, POSSaleItem
    )
    from app.models.medicine_pricing import MedicinePricing  # Pricing module
    
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
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
