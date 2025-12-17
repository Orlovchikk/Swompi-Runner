from swompi.session import engine 
from swompi.models import Base

def initialize_database():
    print("Initializing database...")
    
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()