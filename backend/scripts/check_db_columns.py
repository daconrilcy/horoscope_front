import os
import sys

# Ensure the app can be imported
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, inspect

from app.core.config import settings


def check_columns():
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)

    tables = ["daily_prediction_runs", "daily_prediction_category_scores"]
    for table in tables:
        if not inspector.has_table(table):
            print(f"Table {table} does not exist.")
            continue

        print(f"Table: {table}")
        columns = [c["name"] for c in inspector.get_columns(table)]
        print(f"Columns: {columns}")
        print("-" * 20)


if __name__ == "__main__":
    check_columns()
