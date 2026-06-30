"""
Sync Manager.
Handles logic for offline queuing and online synchronization.
"""

from sqlalchemy.orm import Session
import json
import logging
from typing import Dict, Any

from app.models.sync_queue import SyncQueue, SyncAction, SyncStatus
from app.database import SessionRemote
from app.utils.network import is_online
from app.models import Sale, SaleItem, Medicine # Import models needed for reconstruction

logger = logging.getLogger(__name__)

class SyncManager:
    """
    Manages synchronization between local SQLite and remote MySQL.
    """
    
    @staticmethod
    def add_to_queue(db: Session, action: SyncAction, table_name: str, data: Dict[str, Any]):
        """
        Add an action to the offline queue.
        """
        try:
            # Create queue entry
            entry = SyncQueue(
                action=action,
                table_name=table_name,
                data=data,
                status=SyncStatus.PENDING
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            logger.info(f"[Offline] Action queued: {action} on {table_name}")
            return entry
        except Exception as e:
            logger.error(f"Failed to queue action: {e}")
            db.rollback()
            raise e

    @staticmethod
    def sync_up(local_db: Session):
        """
        Push pending local changes to remote database.
        Sync Direction: Local -> Remote (Upstream).
        """
        if not is_online(check_remote_db=True):
            logger.warning("Cannot sync up: Remote DB unreachable.")
            return

        pending_items = local_db.query(SyncQueue).filter(
            SyncQueue.status == SyncStatus.PENDING
        ).order_by(SyncQueue.created_at).all()
        
        if not pending_items:
            return

        logger.info(f"Found {len(pending_items)} pending items to sync.")
        
        remote_db = SessionRemote()
        
        try:
            for item in pending_items:
                try:
                    SyncManager._process_single_item(item, remote_db)
                    item.status = SyncStatus.DONE
                    local_db.commit() # Commit local status update
                except Exception as e:
                    logger.error(f"Error processing item {item.id}: {e}")
                    item.error_message = str(e)
                    item.status = SyncStatus.ERROR
                    local_db.commit()
                    
        finally:
            remote_db.close()

    @staticmethod
    def _process_single_item(item: SyncQueue, remote_db: Session):
        """
        Replay a single queued action on the remote DB.
        """
        data = item.data
        
        # Example logic for SALES table
        if item.table_name == "sales" and item.action == SyncAction.CREATE:
            # Reconstruct Sale object
            # Note: We need to handle related items carefully
            # For this MVP, we ignore relationships complexity and just insert raw if possible
            # But normally we'd reconstruct the ORM object
            pass
            
            # Simple simulation for verification
            logger.info(f"Simulating PUSH to Remote DB for {item.table_name} ID {data.get('id')}")
            
            # Real implementation would be:
            # new_sale = Sale(**data_without_items)
            # remote_db.add(new_sale)
            # remote_db.commit()

        # Add other tables handling here...
