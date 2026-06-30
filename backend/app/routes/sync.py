"""
Routes de synchronisation cloud — Local SQLite ↔ Supabase PostgreSQL.

Endpoints :
  POST /sync/push    → Pousse les ventes locales vers Supabase
  GET  /sync/pull    → Récupère les mises à jour depuis Supabase
  GET  /sync/status  → État de la synchronisation (nb en attente)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from app.database import get_local_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.sync.sync_manager import SyncManager

router = APIRouter()
logger = logging.getLogger("sync_routes")


@router.post("/push", summary="Pousser les ventes locales vers Supabase")
async def sync_push(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db),
):
    """
    Synchronise les ventes POS locales non-envoyées vers Supabase.
    
    - Lit les POSSale avec sync_status = 'pending' ou 'local_only'
    - Les insère dans Supabase (upsert par UUID)
    - Met à jour sync_status = 'synced' si succès
    
    Retourne un rapport : { synced, errors, online }
    """
    try:
        report = SyncManager.sync_up(local_db=db)
        return {
            "success": True,
            "message": f"{report['synced']} vente(s) synchronisée(s)",
            **report,
        }
    except Exception as e:
        logger.error(f"[/sync/push] Erreur: {e}")
        return {"success": False, "error": str(e), "synced": 0, "online": False}


@router.get("/pull", summary="Récupérer les mises à jour depuis Supabase")
async def sync_pull(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db),
):
    """
    Récupère les paramètres et médicaments depuis Supabase vers la base locale.
    
    Utile après une installation fraîche ou pour synchroniser les
    paramètres de la pharmacie modifiés depuis un autre poste.
    """
    try:
        report = SyncManager.sync_down(local_db=db)
        return {
            "success": True,
            "message": f"{report.get('settings_updated', 0)} paramètre(s) mis à jour",
            **report,
        }
    except Exception as e:
        logger.error(f"[/sync/pull] Erreur: {e}")
        return {"success": False, "error": str(e), "online": False}


@router.get("/status", summary="État de la synchronisation")
async def sync_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db),
):
    """
    Retourne l'état actuel de la synchronisation :
    - online : Supabase accessible ?
    - pending_count : ventes en attente d'envoi
    - error_count : ventes en erreur
    - synced_count : ventes déjà synchronisées
    """
    try:
        return SyncManager.get_status(local_db=db)
    except Exception as e:
        logger.error(f"[/sync/status] Erreur: {e}")
        return {"online": False, "error": str(e)}
