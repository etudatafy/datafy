import argparse
import csv
import psycopg2
import os
import sys
from dotenv import load_dotenv

def load_data(csv_path: str):
    # Load .env file
    load_dotenv()
    db_url = os.getenv("POSTGRE_URL")

    if not db_url:
        print("[ERROR] POSTGRE_URL not found in .env")
        sys.exit(1)

    # Check file exists
    if not os.path.exists(csv_path):
        print(f"[ERROR] File not found: {csv_path}")
        sys.exit(1)

    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        print("[INFO] Connected to database")
    except Exception as e:
        print(f"[ERROR] Could not connect to database: {e}")
        sys.exit(1)

    try:
        # Drop table and enums if they exist
        cursor.execute("""
            DROP TABLE IF EXISTS kaynaklar;

            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'topic_enum') THEN
                    DROP TYPE topic_enum;
                END IF;
                IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kind_enum') THEN
                    DROP TYPE kind_enum;
                END IF;
            END
            $$;
        """)
        print("[INFO] Dropped existing table and enum types")

        # Create enums
        cursor.execute("""
            CREATE TYPE topic_enum AS ENUM (
                'tyt_matematik', 'ayt_matematik', 'geometri',
                'tyt_fizik', 'ayt_fizik', 'tyt_kimya', 'ayt_kimya',
                'tyt_biyoloji', 'ayt_biyoloji',
                'dilbilgisi', 'edebiyat', 'tarih', 'coğrafya'
            );

            CREATE TYPE kind_enum AS ENUM (
                'kolay_kaynak', 'orta_kaynak', 'zor_kaynak', 'link'
            );
        """)
        print("[INFO] Recreated enum types")

        # Create the table
        cursor.execute("""
            CREATE TABLE kaynaklar (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                topic topic_enum NOT NULL,
                kind kind_enum NOT NULL,
                context TEXT NOT NULL,
                description TEXT
            );
        """)
        print("[INFO] Created table 'kaynaklar'")

        # Load and insert CSV
        with open(csv_path, encoding='latin5') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cursor.execute("""
                    INSERT INTO kaynaklar (topic, kind, context, description)
                    VALUES (%s, %s, %s, %s)
                """, (
                    row['topic'].strip(),
                    row['kind'].strip(),
                    row['context'].strip(),
                    row['description'].strip() if row['description'] else None
                ))
                count += 1

        conn.commit()
        print(f"[SUCCESS] Inserted {count} rows into 'kaynaklar'")

    except Exception as e:
        print(f"[ERROR] Failed during execution: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()
        print("[INFO] Database connection closed")

def main():
    parser = argparse.ArgumentParser(description="Load CSV data into PostgreSQL.")
    parser.add_argument("-r", "--read", required=True, help="Path to the CSV file")

    args = parser.parse_args()
    load_data(args.read)

if __name__ == "__main__":
    main()
