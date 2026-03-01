from app.infra.db.base import Base
from app.infra.db.session import engine
# Import all models to register them with Base
from app.infra.db.models import *

def create_tables():
    print("Creating missing tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    create_tables()
