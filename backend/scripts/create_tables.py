from app.infra.db.base import Base

# Import all models to register them with Base
from app.infra.db.models import *  # noqa: F403
from app.infra.db.session import engine


def create_tables():
    print("Creating missing tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


if __name__ == "__main__":
    create_tables()
