from sqlalchemy.orm import Session
from app.database import get_local_db
from app.models.user import User, UserRole
from app.utils.security import hash_password
import sys

def create_super_admin(username, password):
    db = next(get_local_db())
    
    # Check if user exists
    user = db.query(User).filter(User.username == username).first()
    
    if user:
        print(f"User '{username}' found. Updating role to SUPER_ADMIN...")
        user.role = UserRole.SUPER_ADMIN
        user.password_hash = hash_password(password)
        db.commit()
        print(f"User '{username}' updated successfully.")
    else:
        print(f"User '{username}' not found. Creating new SUPER_ADMIN user...")
        new_user = User(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        print(f"User '{username}' created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_super_admin.py <username> <password>")
        print("Example: python create_super_admin.py dev_admin MySecretPass123")
    else:
        create_super_admin(sys.argv[1], sys.argv[2])
