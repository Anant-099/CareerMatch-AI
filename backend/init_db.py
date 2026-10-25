
from database import Base, engine
from models import AnalysisHistory

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
print("Table: analysis_history")
