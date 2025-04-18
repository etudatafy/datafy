import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

env = os.getenv("FLASK_ENV", "production")

if env == "development":
    base_dir = Path(__file__).resolve().parent
    load_dotenv(dotenv_path=base_dir / ".env.development", override=True)

db_uri = os.getenv("DB_ADDRESS")
if not db_uri:
    if env == "development":
        db_uri = "mongodb://127.0.0.1:27017/"
    else:
        raise RuntimeError("Production’da DB_ADDRESS ortam değişkeni tanımlı olmalı.")

print(f"[{env}] Using DB URI: {db_uri}")

client = MongoClient(db_uri)
db = client["yks"]
