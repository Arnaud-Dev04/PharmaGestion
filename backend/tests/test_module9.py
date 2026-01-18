"""
Automated test script for Module 9: Sync.
"""

from app.database import SessionLocal, init_local_db, init_remote_db
from app.sync.sync_manager import SyncManager
from app.models.sync_queue import SyncQueue, SyncAction, SyncStatus

def test_sync_workflow():
    db = SessionLocal()
    
    print("\n=== 1. Initialize DBs (Local & Remote) ===")
    init_local_db()
    try:
        init_remote_db() # Create tables in MySQL
    except Exception as e:
        print(f"[WARN] Remote init warning: {e}")

    print("\n=== 2. Simulate Offline Write (Add to Queue) ===")
    fake_sale_data = {"id": 999, "total_amount": 5000, "payment_method": "CASH"}
    
    try:
        entry = SyncManager.add_to_queue(
            db=db,
            action=SyncAction.CREATE,
            table_name="sales",
            data=fake_sale_data
        )
        print(f"[PASS] Added to queue. ID: {entry.id}, Status: {entry.status}")
    except Exception as e:
        print(f"[FAIL] Add to queue failed: {e}")
        return

    print("\n=== 3. Verify Persistence ===")
    saved_entry = db.query(SyncQueue).filter(SyncQueue.id == entry.id).first()
    if saved_entry and saved_entry.data["total_amount"] == 5000:
        print(f"[PASS] Entry persisted correctly.")
    else:
        print(f"[FAIL] Entry not found or data mismatch.")

    print("\n=== 4. Simulate Sync Up (Process Queue) ===")
    # Note: This requires Remote DB to be "mocked" or available. 
    # Since we don't have a real MySQL set up in this env, we rely on the Simulation log in _process_single_item
    # We will temporarily mock IsOnline to True to force the attempt
    
    # mocking/check online
    import app.sync.sync_manager
    # Force True to bypass check and test the Push logic (even if it errors on DB, it shouldn't remain PENDING if check passed)
    app.sync.sync_manager.is_online = lambda check_remote_db=True: True
    
    print(f"DEBUG: Forced is_online")
    try:
        SyncManager.sync_up(local_db=db)
        # Check status
        db.refresh(saved_entry)
        print(f"[PASS] Sync Up executed. New Status: {saved_entry.status}")
    except Exception as e:
         print(f"[FAIL] Sync Up failed: {e}")
    
    # Cleanup
    db.delete(saved_entry)
    db.commit()
    db.close()

if __name__ == "__main__":
    test_sync_workflow()
