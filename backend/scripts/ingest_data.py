"""
Dataset ingestion script for crime data
Uses public Chicago Crime Dataset as example
Can be adapted for any time-series crime dataset
"""
import pandas as pd
import requests
from datetime import datetime
from sqlalchemy.orm import Session
import random

from app.database import SessionLocal, engine, Base
from app.models.crime import Crime


def download_chicago_crime_data(limit: int = 10000):
    """
    Download sample data from Chicago Crime Data API
    API Docs: https://data.cityofchicago.org/
    """
    print(f"Downloading {limit} crime records from Chicago Crime Dataset...")
    
    # Chicago Data Portal API endpoint
    # Using sample data for demonstration
    url = f"https://data.cityofchicago.org/resource/crimes.json?$limit={limit}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"Downloaded {len(data)} records")
        return data
    except Exception as e:
        print(f"Failed to download data: {e}")
        print("Generating synthetic sample data instead...")
        return generate_synthetic_data(limit)


def generate_synthetic_data(count: int = 1000):
    """
    Generate synthetic crime data for Hyderabad, India and Chicago, USA
    70% Hyderabad, 30% Chicago for Indian focus
    """
    import random
    from datetime import timedelta
    
    # Indian crime types (IPC sections and common crimes)
    india_crime_types = [
        "THEFT", "CHAIN SNATCHING", "HOUSE BURGLARY", "ASSAULT", 
        "EVE TEASING", "MOTOR VEHICLE THEFT", "ROBBERY", 
        "CYBERCRIME", "FRAUD", "DRUNK DRIVING", "PICKPOCKETING",
        "MOBILE THEFT", "DOMESTIC VIOLENCE", "PROPERTY DISPUTE",
        "CHEATING", "KIDNAPPING", "RIOTING"
    ]
    
    chicago_crime_types = [
        "THEFT", "BATTERY", "CRIMINAL DAMAGE", "ASSAULT", "BURGLARY",
        "MOTOR VEHICLE THEFT", "ROBBERY", "DECEPTIVE PRACTICE", 
        "NARCOTICS", "OTHER OFFENSE"
    ]
    
    # Hyderabad coordinates (major areas)
    # Covers: Madhapur, Gachibowli, Hitech City, Begumpet, Secunderabad, Old City
    hyd_areas = [
        {"name": "Madhapur", "lat": (17.445, 17.455), "lng": (78.385, 78.400)},
        {"name": "Gachibowli", "lat": (17.435, 17.445), "lng": (78.345, 78.360)},
        {"name": "Hitech City", "lat": (17.445, 17.455), "lng": (78.370, 78.390)},
        {"name": "Begumpet", "lat": (17.440, 17.450), "lng": (78.460, 78.475)},
        {"name": "Secunderabad", "lat": (17.435, 17.445), "lng": (78.495, 78.510)},
        {"name": "Banjara Hills", "lat": (17.410, 17.425), "lng": (78.440, 78.455)},
        {"name": "Kukatpally", "lat": (17.485, 17.500), "lng": (78.390, 78.405)},
        {"name": "LB Nagar", "lat": (17.335, 17.350), "lng": (78.545, 78.560)},
        {"name": "Dilsukhnagar", "lat": (17.365, 17.380), "lng": (78.520, 78.535)},
        {"name": "Charminar (Old City)", "lat": (17.355, 17.370), "lng": (78.465, 78.480)}
    ]
    
    # Chicago coordinates
    chi_lat_min, chi_lat_max = 41.6, 42.0
    chi_lng_min, chi_lng_max = -87.9, -87.5
    
    base_date = datetime.utcnow() - timedelta(days=365)
    
    data = []
    
    # Generate 70% Hyderabad crimes
    hyd_count = int(count * 0.7)
    for i in range(hyd_count):
        area = random.choice(hyd_areas)
        crime_type = random.choice(india_crime_types)
        date = base_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        data.append({
            "id": f"HYD{i:07d}",
            "primary_type": crime_type,
            "description": f"{crime_type} in {area['name']}, Hyderabad",
            "latitude": round(random.uniform(area['lat'][0], area['lat'][1]), 6),
            "longitude": round(random.uniform(area['lng'][0], area['lng'][1]), 6),
            "date": date.isoformat(),
            "arrest": random.random() < 0.15,  # Lower arrest rate in India
            "domestic": random.random() < 0.12,
            "district": area['name'],
            "ward": random.randint(1, 150),  # GHMC has 150 wards
            "location_description": random.choice([
                "STREET", "RESIDENCE", "APARTMENT", "TECH PARK",
                "METRO STATION", "SHOPPING MALL", "RESTAURANT", 
                "BUS STOP", "HIGHWAY", "MARKET"
            ]),
            "city": "Hyderabad"
        })
    
    # Generate 30% Chicago crimes
    chi_count = count - hyd_count
    for i in range(chi_count):
        crime_type = random.choice(chicago_crime_types)
        date = base_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        data.append({
            "id": f"CHI{i:07d}",
            "primary_type": crime_type,
            "description": f"Chicago {crime_type.lower()} incident",
            "latitude": round(random.uniform(chi_lat_min, chi_lat_max), 6),
            "longitude": round(random.uniform(chi_lng_min, chi_lng_max), 6),
            "date": date.isoformat(),
            "arrest": random.random() < 0.2,
            "domestic": random.random() < 0.15,
            "district": str(random.randint(1, 25)),
            "ward": random.randint(1, 50),
            "location_description": random.choice([
                "STREET", "RESIDENCE", "APARTMENT", "SIDEWALK",
                "PARKING LOT", "RESTAURANT", "COMMERCIAL BUILDING"
            ]),
            "city": "Chicago"
        })
    
    print(f"Generated {hyd_count} Hyderabad records and {chi_count} Chicago records")
    return data


def parse_crime_record(record: dict) -> dict:
    """Parse a crime record into our database format"""
    try:
        # Handle both real API data and synthetic data
        occurred_at = None
        if "date" in record:
            try:
                occurred_at = datetime.fromisoformat(record["date"].replace("Z", "+00:00"))
            except:
                occurred_at = datetime.strptime(record["date"][:19], "%Y-%m-%dT%H:%M:%S")
        
        return {
            "case_id": str(record.get("id", record.get("case_number", f"UNK{random.randint(1000000, 9999999)}"))),
            "crime_type": record.get("primary_type", "UNKNOWN"),
            "description": record.get("description", ""),
            "latitude": float(record.get("latitude", 0)) or None,
            "longitude": float(record.get("longitude", 0)) or None,
            "location_description": record.get("location_description", ""),
            "occurred_at": occurred_at or datetime.utcnow(),
            "arrest_made": record.get("arrest", False),
            "domestic": record.get("domestic", False),
            "district": record.get("district"),
            "ward": record.get("ward"),
            "user_reported": False
        }
    except Exception as e:
        print(f"Error parsing record: {e}")
        return None


def ingest_data(data: list, db: Session):
    """Ingest crime data into database"""
    print(f"\nIngesting {len(data)} records into database...")
    
    inserted_count = 0
    skipped_count = 0
    
    for record in data:
        parsed = parse_crime_record(record)
        
        if not parsed or not parsed["latitude"] or not parsed["longitude"]:
            skipped_count += 1
            continue
        
        # Check if record already exists
        existing = db.query(Crime).filter(Crime.case_id == parsed["case_id"]).first()
        if existing:
            skipped_count += 1
            continue
        
        # Create new crime record
        crime_record = Crime(**parsed)
        db.add(crime_record)
        inserted_count += 1
        
        # Commit in batches
        if inserted_count % 100 == 0:
            db.commit()
            print(f"Inserted {inserted_count} records...")
    
    # Final commit
    db.commit()
    
    print(f"\n✓ Ingestion complete!")
    print(f"  - Inserted: {inserted_count}")
    print(f"  - Skipped: {skipped_count}")
    print(f"  - Total: {inserted_count + skipped_count}")


def main():
    """Main ingestion function"""
    print("=" * 60)
    print("Crime Dataset Ingestion Script")
    print("=" * 60)
    
    # Create tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    # Download data
    data = download_chicago_crime_data(limit=5000)
    
    if not data:
        print("No data to ingest")
        return
    
    # Ingest data
    db = SessionLocal()
    try:
        ingest_data(data, db)
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("Dataset ingestion completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
