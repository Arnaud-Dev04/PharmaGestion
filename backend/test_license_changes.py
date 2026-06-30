"""
Test script to verify license management changes
"""
import sys
sys.path.insert(0, 'c:/Pharma_logiciels_version_01/backend')

try:
    print("Testing imports...")
    from app.auth.dependencies import get_super_admin_user_bypass_license
    print("✓ get_super_admin_user_bypass_license imported successfully")
    
    from app.routes.license import router
    print("✓ license router imported successfully")
    
    from app.routes import license_router
    print("✓ license_router from routes package imported successfully")
    
    print("\n✅ All imports successful! No syntax errors detected.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
