Module 1: Backend Structure + Database + Models
Overview
Setting up the foundational structure for a pharmacy management system with dual-database support (SQLite for offline, MySQL for online sync). All models will include timestamp fields for conflict resolution in future synchronization logic.

User Review Required
IMPORTANT

Dual Database Architecture: This implementation sets up TWO database connections (SQLite local and MySQL remote). The synchronization logic will come in Module 9, but the infrastructure is being prepared now.

WARNING

Python Version: The project context specifies Python 3.10.11. Please ensure this version is installed in your environment.

Proposed Changes
Configuration Files
[NEW]
requirements.txt
Complete dependency list including:

FastAPI ecosystem (fastapi, uvicorn)
Database (sqlalchemy, pymysql for MySQL support)
Security (python-jose, passlib)
File handling (python-multipart, reportlab, openpyxl)
Migrations (alembic)
Environment variables (python-dotenv)
[NEW]
.env.example
Template for environment configuration with:

DB_URL_LOCAL: SQLite connection string
DB_URL_REMOTE: MySQL connection string (XAMPP compatible)
SECRET_KEY: JWT secret
ALGORITHM: JWT algorithm (HS256)
[NEW]
README.md
Installation and setup instructions including:

Prerequisites
Environment setup
Database initialization
Running the application
Project structure overview
Database Layer
[NEW]
core.py
SQLAlchemy configuration with:

Base declarative class for models
SessionLocal factory for SQLite (offline)
SessionRemote factory for MySQL (online)
Dependency injection functions (get_local_db(), get_remote_db())
Database initialization helpers
[NEW]
init
.py
Database package initialization exposing Base and session factories.

Data Models
All models will inherit from a common mixin providing:

id: Primary key
created_at: Timestamp for creation
updated_at: Timestamp for last modification (auto-updating)
[NEW]
base.py
Base mixin class with:

id, created_at, updated_at fields
Auto-generated UUID or auto-increment IDs
Timestamp auto-management
[NEW]
user.py
User model with fields:

username: Unique identifier
password_hash: Hashed password
role: Enum (admin/pharmacist)
is_active: Boolean flag
[NEW]
medicine.py
Three models:

MedicineFamily: Dynamic categories (id, name)
MedicineType: Package types - Plaquette, Flacon, etc. (id, name)
Medicine: Main product model
code: Unique product code
name: Product name
family_id, type_id: Foreign keys
quantity: Current stock
price_buy, price_sell: Pricing
expiry_date: Expiration tracking
min_stock_alert: Low stock threshold
[NEW]
supplier.py
Supplier model with:

name: Company name
phone, email: Contact info
contact_name: Person to contact
[NEW]
customer.py
Customer model with:

first_name, last_name: Customer identity
phone: Unique identifier
total_points: Loyalty bonus points
[NEW]
sales.py
Two models:

Sale: Header
code: Invoice number (auto-generated)
total_amount: Total in FBu
payment_method: Cash/Card/etc.
date: Transaction timestamp
user_id: Seller reference
customer_id: Optional customer
sync_status: Enum (synced/pending)
SaleItem: Line items
sale_id: Parent sale
medicine_id: Product sold
quantity, unit_price, total_price: Line data
[NEW]
restock.py
Two models:

RestockOrder: Header
supplier_id: Source supplier
status: Draft/Confirmed/Received
date: Order date
total_amount: Order value
RestockItem: Line items
order_id: Parent order
medicine_id: Product ordered
quantity, price_buy: Line data
[NEW]
settings.py
Settings model (key-value store):

key: Setting identifier
value: JSON or text value
For: pharmacy name, logo, bonus %, currency, etc.
[NEW]
sync_log.py
SyncLog model (debugging sync):

timestamp: Log time
status: Success/Failure
message: Details
[NEW]
init
.py
Central import file exposing all models for easy import.

Application Entry
[NEW]
main.py
FastAPI application with:

App initialization
Database table creation on startup
Basic health check endpoint
CORS middleware for React frontend
[NEW]
init
.py
App package initialization.

Verification Plan
Automated Tests
Since this is Module 1 (foundation), comprehensive unit tests will be added in Module 10. For now, verification focuses on:

Database Initialization Test

python -c "from app.database.core import init_local_db; init_local_db(); print('SQLite DB initialized successfully')"
Model Import Test

python -c "from app.models import User, Medicine, Sale, Settings; print('All models imported successfully')"
Application Startup Test

uvicorn main:app --reload
Access http://localhost:8000/docs to verify Swagger UI loads
Access http://localhost:8000/health to verify health check endpoint
Manual Verification
Verify folder structure exists with all required directories

Check requirements.txt can be installed without errors:

pip install -r requirements.txt
Review .env.example and create .env file with actual values

Inspect SQLite database after initialization:

sqlite3 pharmacy_local.db ".tables"
Should show all created tables: users, medicines, medicine_families, medicine_types, suppliers, customers, sales, sale_items, restock_orders, restock_items, settings, sync_logs

MySQL connection (optional for now, will be fully utilized in Module 9):

Verify connection string format is correct for XAMPP MySQL
Database creation will be tested when MySQL is actively needed
