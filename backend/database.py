import os
import re
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pymongo import MongoClient

env = os.getenv("FLASK_ENV", "production")

if env == "development":
    base_dir = Path(__file__).resolve().parent
    load_dotenv(dotenv_path=base_dir / ".env.development", override=True)

raw_uri = os.getenv("DB_ADDRESS")
if not raw_uri:
    if env == "development":
        raw_uri = "mongodb://127.0.0.1:27017/"
    else:
        raise RuntimeError("Production’da DB_ADDRESS ortam değişkeni tanımlı olmalı.")

def encode_mongo_uri(uri: str) -> str:
    pattern = r'^(mongodb(?:\+srv)?://)([^:/]+):([^@]+)@(.*)$'
    m = re.match(pattern, uri)
    if m:
        prefix, user, pwd, rest = m.groups()
        pwd_enc = quote_plus(pwd)
        return f"{prefix}{user}:{pwd_enc}@{rest}"
    return uri

db_uri = encode_mongo_uri(raw_uri)
print(f"[{env}] Using DB URI: {db_uri}")

client = MongoClient(db_uri)
db = client["yks"]
