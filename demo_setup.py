# demo_setup.py
import psycopg2
from dotenv import load_dotenv
import os
from ingestion.embedder import ingest_directory

load_dotenv()

def clear_all_documents():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("DELETE FROM documents")
    conn.commit()
    cur.close()
    conn.close()
    print("Cleared all documents from database")

def setup_demo(industry: str):
    folder = f"data/demo_{industry}"
    if not os.path.exists(folder):
        print(f"Folder not found: {folder}")
        return
    clear_all_documents()
    ingest_directory(folder)
    print(f"\nDemo ready for: {industry}")

if __name__ == "__main__":
    import sys
    industry = sys.argv[1] if len(sys.argv) > 1 else "manufacturing"
    setup_demo(industry)