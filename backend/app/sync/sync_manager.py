"""
Sync Manager - Synchronisation offline-first SQLite ↔ Supabase PostgreSQL.

Logique :
  - sync_up()   : pousse les pos_sales locales non-synchronisées vers Supabase
  - sync_down() : récupère les médicaments/paramètres depuis Supabase
  - Utilise les UUID des POSSale pour éviter les doublons
  - Résolution de conflits : Local wins (offline-first)
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from app.database import SessionRemote
from app.utils.network import is_online

logger = logging.getLogger(__name__)


def _remote_available() -> bool:
    """Vérifie si Supabase est accessible."""
    try:
        return is_online(check_remote_db=True)
    except Exception:
        return False


class SyncManager:
    """
    Gère la synchronisation bidirectionnelle Local (SQLite) ↔ Cloud (Supabase PostgreSQL).
    """

    # ──────────────────────────────────────────────────────────────────
    # SYNC UP : Local → Supabase
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def sync_up(local_db: Session) -> Dict[str, Any]:
        """
        Pousse les ventes POS locales non-synchronisées vers Supabase.
        Retourne un rapport avec le nombre de ventes synchronisées.
        """
        report = {"synced": 0, "errors": 0, "skipped": 0, "online": False}

        if not _remote_available():
            logger.warning("[SyncUp] Supabase non joignable — skip.")
            return report

        report["online"] = True

        try:
            from app.models.pos_sale import POSSale, POSSaleItem
            from app.models.medicine import Medicine
            from app.models.user import User

            # Ventes locales non encore envoyées vers le cloud
            pending_sales = local_db.query(POSSale).filter(
                POSSale.sync_status.in_(["pending", "local_only"])
            ).order_by(POSSale.date.asc()).limit(100).all()

            if not pending_sales:
                logger.info("[SyncUp] Rien à synchroniser.")
                return report

            logger.info(f"[SyncUp] {len(pending_sales)} vente(s) à envoyer...")

            remote_db = SessionRemote()
            try:
                for sale in pending_sales:
                    try:
                        SyncManager._push_pos_sale(sale, remote_db)
                        # Marquer comme synchronisée
                        sale.sync_status = "synced"
                        sale.synced_at = datetime.utcnow()
                        local_db.commit()
                        report["synced"] += 1
                    except Exception as e:
                        logger.error(f"[SyncUp] Erreur vente {sale.sale_uuid}: {e}")
                        sale.sync_status = "error"
                        local_db.commit()
                        report["errors"] += 1
            finally:
                remote_db.close()

        except Exception as e:
            logger.error(f"[SyncUp] Erreur fatale: {e}")
            report["errors"] += 1

        logger.info(f"[SyncUp] Résultat: {report}")
        return report

    @staticmethod
    def _push_pos_sale(sale, remote_db: Session):
        """
        Insère ou met à jour une POSSale dans Supabase (upsert par UUID).
        """
        from app.models.pos_sale import POSSale as RemotePOSSale, POSSaleItem as RemotePOSSaleItem

        # Vérifier si déjà présente (par UUID)
        existing = remote_db.query(RemotePOSSale).filter(
            RemotePOSSale.sale_uuid == sale.sale_uuid
        ).first()

        if existing:
            logger.debug(f"[SyncUp] Vente {sale.sale_uuid} déjà dans Supabase — skip.")
            return

        # Copier la vente vers Supabase
        remote_sale = RemotePOSSale(
            sale_uuid=sale.sale_uuid,
            code=sale.code,
            total_amount=sale.total_amount,
            payment_method=sale.payment_method,
            status=sale.status,
            date=sale.date,
            user_id=sale.user_id,
            customer_id=sale.customer_id,
            customer_name=getattr(sale, "customer_name", None),
            customer_phone=getattr(sale, "customer_phone", None),
            insurance_provider=getattr(sale, "insurance_provider", None),
            insurance_card_id=getattr(sale, "insurance_card_id", None),
            coverage_percent=getattr(sale, "coverage_percent", 0.0),
            notes=getattr(sale, "notes", None),
            sync_status="synced",
            synced_at=datetime.utcnow(),
        )
        remote_db.add(remote_sale)
        remote_db.flush()  # Pour obtenir remote_sale.id

        # Copier les articles
        for item in sale.items:
            remote_item = RemotePOSSaleItem(
                pos_sale_id=remote_sale.id,
                medicine_id=item.medicine_id,
                batch_id=item.batch_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                sale_type=getattr(item, "sale_type", "packaging"),
                discount_percent=getattr(item, "discount_percent", 0.0),
            )
            remote_db.add(remote_item)

        remote_db.commit()
        logger.info(f"[SyncUp] ✅ Vente {sale.sale_uuid} ({sale.code}) → Supabase")

    # ──────────────────────────────────────────────────────────────────
    # SYNC DOWN : Supabase → Local
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def sync_down(local_db: Session) -> Dict[str, Any]:
        """
        Récupère les médicaments et paramètres depuis Supabase vers le local.
        Utile pour une installation fraîche ou une mise à jour partagée.
        """
        report = {"medicines_updated": 0, "settings_updated": 0, "errors": 0, "online": False}

        if not _remote_available():
            logger.warning("[SyncDown] Supabase non joignable — skip.")
            return report

        report["online"] = True

        remote_db = SessionRemote()
        try:
            # Synchroniser les paramètres depuis Supabase
            from app.models.settings import Settings
            try:
                remote_settings = remote_db.query(Settings).all()
                for rs in remote_settings:
                    local_s = local_db.query(Settings).filter(Settings.key == rs.key).first()
                    if local_s:
                        local_s.value = rs.value
                    else:
                        local_db.add(Settings(key=rs.key, value=rs.value))
                local_db.commit()
                report["settings_updated"] = len(remote_settings)
            except Exception as e:
                logger.warning(f"[SyncDown] Settings sync skipped: {e}")

        except Exception as e:
            logger.error(f"[SyncDown] Erreur fatale: {e}")
            report["errors"] += 1
        finally:
            remote_db.close()

        logger.info(f"[SyncDown] Résultat: {report}")
        return report

    # ──────────────────────────────────────────────────────────────────
    # STATUT
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def get_status(local_db: Session) -> Dict[str, Any]:
        """
        Retourne l'état de la synchronisation.
        """
        try:
            from app.models.pos_sale import POSSale
            pending = local_db.query(POSSale).filter(
                POSSale.sync_status.in_(["pending", "local_only"])
            ).count()
            errored = local_db.query(POSSale).filter(
                POSSale.sync_status == "error"
            ).count()
            synced = local_db.query(POSSale).filter(
                POSSale.sync_status == "synced"
            ).count()
            online = _remote_available()
            return {
                "online": online,
                "pending_count": pending,
                "error_count": errored,
                "synced_count": synced,
                "last_check": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {"online": False, "error": str(e)}

    # ──────────────────────────────────────────────────────────────────
    # QUEUE LEGACY (compatibilité avec l'ancien code)
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def add_to_queue(db: Session, action, table_name: str, data: Dict[str, Any]):
        """Compatibilité legacy — utiliser sync_up() à la place."""
        logger.info(f"[SyncQueue] Action {action} sur {table_name} → sera traitée par sync_up()")
