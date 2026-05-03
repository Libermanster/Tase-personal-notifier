import os
import requests
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from sqlmodel import Session, select, func
from src.database import engine, init_db
from src.models import Company

def get_headers():
    load_dotenv()
    api_key = os.getenv("TASE_API_KEY")
    if not api_key:
        raise ValueError("TASE_API_KEY not found in .env")
    
    return {
        "apikey": api_key,
        "Accept": "application/json",
        "Accept-Language": "en-US", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

def fetch_companies():
    """
    Fetches the list of companies from TASE DataWise.
    """
    url = "https://datawise.tase.co.il/v1/basic-securities/companies-list"
    print(f"Fetching companies from {url}...")
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        data = response.json()
        companies = data.get('companiesList', {}).get('result', [])
        return companies
    except Exception as e:
        print(f"Error fetching companies: {e}")
        return []

def save_companies_to_db(companies_data):
    """
    Saves or updates fetched companies in the PostgreSQL database.
    """
    print(f"Saving {len(companies_data)} companies to the database...")
    count_new = 0
    count_updated = 0
    
    with Session(engine) as session:
        for item in companies_data:
            issuer_id = item.get('issuerId')
            if not issuer_id:
                continue
            
            # Check if company already exists
            statement = select(Company).where(Company.issuer_id == issuer_id)
            db_company = session.exec(statement).first()
            
            if db_company:
                # Update existing record
                db_company.name = item.get('companyName', db_company.name)
                db_company.sector = item.get('taseSector', db_company.sector)
                db_company.last_updated = datetime.now().isoformat()
                session.add(db_company)
                count_updated += 1
            else:
                # Create new record
                new_company = Company(
                    issuer_id=issuer_id,
                    name=item.get('companyName', 'N/A'),
                    sector=item.get('taseSector'),
                    last_updated=datetime.now().isoformat()
                )
                session.add(new_company)
                count_new += 1
        
        session.commit()
    
    print(f"Database sync complete: {count_new} new, {count_updated} updated.")

def export_to_sql():
    """
    Exports the PostgreSQL database to a .sql file using pg_dump.
    """
    load_dotenv()
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "db")
    db_name = os.getenv("POSTGRES_DB", "tase_notifier")
    
    os.makedirs("data", exist_ok=True)
    filename = f"data/tase_backup.sql"
    
    print(f"Exporting database to {filename}...")
    
    # Set PGPASSWORD environment variable for pg_dump
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    try:
        command = [
            "pg_dump",
            "-h", host,
            "-U", user,
            "-d", db_name,
            "-f", filename,
            "--no-owner",
            "--no-privileges"
        ]
        subprocess.run(command, env=env, check=True)
        print(f"Export successful!")
    except Exception as e:
        print(f"Error exporting database: {e}")

def main():
    print("TASE Personal Notifier - Database Sync")
    
    # Initialize the database tables
    init_db()
    
    # Fetch data
    companies_data = fetch_companies()
    
    if companies_data:
        # Persist to Postgres
        save_companies_to_db(companies_data)
        
        # Verify a quick count
        with Session(engine) as session:
            count = session.exec(select(func.count(Company.id))).one()
            print(f"Total companies in database: {count}")
            
        # Export to SQL file
        export_to_sql()
    else:
        print("No data fetched. Skipping database sync.")

if __name__ == "__main__":
    main()
