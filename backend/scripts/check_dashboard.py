
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.append(os.getcwd())

try:
    from app.database import Base, get_local_db
    from app.services import dashboard_service
    
    # Create session manually
    SQLALCHEMY_DATABASE_URL = "sqlite:///./pharmacy_local.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    print("Testing get_stats()...")
    stats = dashboard_service.get_stats(db)
    print("Stats retrieved successfully")
    
    print("Testing get_revenue_chart_data()...")
    chart = dashboard_service.get_revenue_chart_data(db)
    print("Chart data retrieved successfully")

    print("Validating with Pydantic schema...")
    from app.schemas.dashboard import DashboardStatsResponse
    
    response_data = {
        **stats,
        "revenue_chart": chart
    }
    
    validated = DashboardStatsResponse(**response_data)
    print("Pydantic validation SUCCESS!")
    print(validated.model_dump())

except Exception as e:
    import traceback
    print("ERROR OCCURRED:")
    traceback.print_exc()
