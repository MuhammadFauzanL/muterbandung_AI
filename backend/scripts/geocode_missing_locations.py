import os
import sys
import time
import requests
from urllib.parse import quote_plus

# Add backend directory to sys.path so we can import app modules
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.destination import Destination
from app.models.accommodation import Accommodation

from typing import Optional

def geocode_location(name: str) -> Optional[tuple[float, float]]:
    """Fetch coordinates from Nominatim API for a given location name."""
    try:
        query = quote_plus(f"{name} Bandung Indonesia")
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        headers = {
            "User-Agent": "MuterBandung-DataFill-Script/1.0",
            "Accept-Language": "id"
        }
        
        # Respect Nominatim rate limit (1 request per second strictly)
        time.sleep(1.2)
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"  [!] Geocoding error for '{name}': {e}")
    
    return None

def main():
    print("Starting Geocoding Data Backfill Script...")
    db: Session = SessionLocal()
    try:
        # Process Destinations
        destinations = db.query(Destination).filter(
            (Destination.latitude == None) | (Destination.longitude == None)
        ).all()
        
        print(f"Found {len(destinations)} destinations missing coordinates.")
        for dest in destinations:
            print(f"Geocoding Destination: {dest.name}...")
            coords = geocode_location(dest.name)
            if coords:
                dest.latitude, dest.longitude = coords
                print(f"  [+] Found coords: {coords}")
            else:
                print(f"  [-] Coords not found for: {dest.name}")
        
        # Process Accommodations
        accommodations = db.query(Accommodation).filter(
            (Accommodation.latitude == None) | (Accommodation.longitude == None)
        ).all()
        
        print(f"\nFound {len(accommodations)} accommodations missing coordinates.")
        for acc in accommodations:
            print(f"Geocoding Accommodation: {acc.name}...")
            coords = geocode_location(acc.name)
            if coords:
                acc.latitude, acc.longitude = coords
                print(f"  [+] Found coords: {coords}")
            else:
                print(f"  [-] Coords not found for: {acc.name}")
                
        # Commit all changes to database
        db.commit()
        print("\nAll changes have been successfully committed to the database.")
        
    except Exception as e:
        db.rollback()
        print(f"Script aborted due to error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
