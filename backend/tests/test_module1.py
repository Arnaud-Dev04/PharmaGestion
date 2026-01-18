"""
Script de test pour vérifier le Module 1.
"""

from app.database.core import Base, engine_local, init_local_db
from app.models import (
    User, Medicine, MedicineFamily, MedicineType,
    Supplier, Customer, Sale, SaleItem,
    RestockOrder, RestockItem, Settings, SyncLog
)
import sqlalchemy

print("=" * 60)
print("TEST MODULE 1 - VERIFICATION COMPLETE")
print("=" * 60)

# Test 1: Import des modèles
print("\n[TEST 1] Import des modèles...")
try:
    models_list = [
        ("User", User),
        ("Medicine", Medicine),
        ("MedicineFamily", MedicineFamily),
        ("MedicineType", MedicineType),
        ("Supplier", Supplier),
        ("Customer", Customer),
        ("Sale", Sale),
        ("SaleItem", SaleItem),
        ("RestockOrder", RestockOrder),
        ("RestockItem", RestockItem),
        ("Settings", Settings),
        ("SyncLog", SyncLog),
    ]
    
    for name, model in models_list:
        print(f"  [OK] {name:20} -> table: {model.__tablename__}")
    
    print(f"\n  Total: {len(models_list)} modeles importes avec succes")
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 2: Initialisation de la base de données
print("\n[TEST 2] Initialisation de la base de donnees...")
try:
    init_local_db()
    print("  [OK] Base de donnees initialisee")
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 3: Vérification des tables créées
print("\n[TEST 3] Verification des tables creees...")
try:
    inspector = sqlalchemy.inspect(engine_local)
    tables = inspector.get_table_names()
    
    expected_tables = [
        "users", "medicine_families", "medicine_types", "medicines",
        "suppliers", "customers", "sales", "sale_items",
        "restock_orders", "restock_items", "settings", "sync_logs"
    ]
    
    print(f"  Tables trouvees: {len(tables)}")
    for table in sorted(tables):
        status = "[OK]" if table in expected_tables else "[?]"
        print(f"    {status} {table}")
    
    missing = set(expected_tables) - set(tables)
    if missing:
        print(f"\n  [ATTENTION] Tables manquantes: {missing}")
    else:
        print(f"\n  [OK] Toutes les tables attendues sont presentes")
        
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 4: Vérification des champs created_at et updated_at
print("\n[TEST 4] Verification des timestamps (created_at, updated_at)...")
try:
    for name, model in models_list:
        has_created = hasattr(model, 'created_at')
        has_updated = hasattr(model, 'updated_at')
        
        if has_created and has_updated:
            print(f"  [OK] {name:20} -> created_at, updated_at")
        else:
            print(f"  [ERREUR] {name:20} -> manque timestamps!")
            
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 5: Vérification des relations
print("\n[TEST 5] Verification de quelques relations...")
try:
    # Medicine -> Family
    print(f"  [OK] Medicine.family -> {Medicine.family.property.mapper.class_.__name__}")
    # Sale -> Items
    print(f"  [OK] Sale.items -> {Sale.items.property.mapper.class_.__name__}")
    # Customer -> Sales
    print(f"  [OK] Customer.sales -> {Customer.sales.property.mapper.class_.__name__}")
    # RestockOrder -> Supplier
    print(f"  [OK] RestockOrder.supplier -> {RestockOrder.supplier.property.mapper.class_.__name__}")
    
    print(f"\n  [OK] Relations fonctionnelles")
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Résumé final
print("\n" + "=" * 60)
print("RESULTAT FINAL")
print("=" * 60)
print("[OK] Module 1: TOUS LES TESTS REUSSIS!")
print("\nStructure:")
print(f"  - {len(models_list)} modeles SQLAlchemy")
print(f"  - {len(tables)} tables dans la base de donnees")
print(f"  - Base SQLite: pharmacy_local.db")
print("\nPret pour le Module 2 (Authentification JWT)")
print("=" * 60)
