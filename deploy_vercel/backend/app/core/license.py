from datetime import datetime
from .config import LICENSE_EXPIRATION_DATE, WARNING_DAYS_THRESHOLD

from sqlalchemy.orm import Session
from app.models.settings import Settings

class LicenseService:
    @staticmethod
    def get_license_status(db: Session = None):
        expiration_date_str = LICENSE_EXPIRATION_DATE
        
        warning_days = WARNING_DAYS_THRESHOLD
        warning_msg = "Votre licence expire bientôt. Veuillez contacter le concepteur pour une mise à jour."
        
        # Try to get from DB if session is provided
        if db:
            try:
                # 1. Expiration Date
                setting = db.query(Settings).filter(Settings.key == "license_expiry_date").first()
                if setting and setting.value:
                    expiration_date_str = setting.value
                
                # 2. Warning Days Threshold
                setting = db.query(Settings).filter(Settings.key == "license_warning_bdays").first()
                if setting and setting.value:
                    try:
                        warning_days = int(setting.value)
                    except:
                        pass
                
                # 3. Warning Message
                setting = db.query(Settings).filter(Settings.key == "license_warning_message").first()
                if setting and setting.value:
                    warning_msg = setting.value
                    
            except Exception:
                pass # Fallback to config

        try:
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
            today = datetime.now()
            
            # Calculate days remaining
            delta = expiration_date - today
            days_remaining = delta.days + 1 # Include today
            
            if days_remaining < 0:
                return {
                    "status": "expired",
                    "days_remaining": 0,
                    "expiration_date": expiration_date_str,
                    "message": warning_msg
                }
            
            if days_remaining <= warning_days:
                return {
                    "status": "warning",
                    "days_remaining": days_remaining,
                    "expiration_date": expiration_date_str,
                    "message": warning_msg
                }
                
            return {
                "status": "valid",
                "days_remaining": days_remaining,
                "expiration_date": expiration_date_str,
                "message": "Licence valide."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur de vérification de licence: {str(e)}"
            }

    @staticmethod
    def check_license_validity(db: Session = None) -> bool:
        """Returns True if license is valid, False otherwise."""
        status = LicenseService.get_license_status(db)
        return status["status"] != "expired"

license_service = LicenseService()
