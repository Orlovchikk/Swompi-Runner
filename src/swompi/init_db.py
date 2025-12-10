from session import engine 
from models import Base

def initialize_database():
    print("Initializing database...")
    
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()