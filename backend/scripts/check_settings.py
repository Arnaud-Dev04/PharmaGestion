from app.database import get_local_db
from app.models.settings import Settings

db = next(get_local_db())
s = db.query(Settings).filter(Settings.key == "license_warning_message").first()
print(f"Key: {s.key}, Value: '{s.value}'" if s else "Key not found")
