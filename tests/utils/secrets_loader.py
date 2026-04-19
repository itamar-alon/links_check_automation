# secrets_loader.py

import os
from dotenv import load_dotenv
from pathlib import Path

def load_secrets():
    """
    Loads configuration data from a .env file using an absolute path calculation.
    The code assumes that the .env file is located in the project root,
    three levels above this file.
    """
    
    # 1. Determine the absolute path of the secrets_loader.py file
    script_path = Path(__file__).resolve() 
    
    # 2. Calculate the project root (move up from utils/ to tests/ and then to links/)
    project_root = script_path.parent.parent.parent
    
    # 3. Build the full path to the .env file
    dotenv_path = project_root / ".env"
    
    # Print the path being passed to load_dotenv()
    print(f"*** Attempting to load .env from absolute path: {dotenv_path}") 
    
    # Load environment variables from .env file
    load_dotenv(dotenv_path=dotenv_path)

    # Retrieve all credentials using os.getenv()
    secrets = {
        'business_url': os.getenv('BUSINESS_URL'),
        'daycare_url': os.getenv('DAYCARE_URL'),
        'education_url': os.getenv('EDUCATION_URL'),
        'enforcement_url': os.getenv('ENFORCEMENT_URL'),
        'login_url': os.getenv('LOGIN_URL'),
        'parking_url': os.getenv('PARKING_URL'),
        'street_url': os.getenv('STREET_URL'),
        'water_url': os.getenv('WATER_URL'),
        'home_url_part': os.getenv('HOME_URL_PART'),
        'user_data': {
            'id_number': os.getenv('ID_NUMBER'),
            'password': os.getenv('PASSWORD')
        }
    }

    # Basic validation to ensure essential variables are loaded
    if not secrets['business_url']: # Check one of the URLs as a sample
        print(f"❌ Error: Environment variables not found. Ensure .env file exists at {dotenv_path} and is configured correctly.")
        return None
        
    return secrets

# --- Verification ---
if __name__ == '__main__':
    data = load_secrets()
    if data:
        print("\n✅ Secrets loading successful!")
        # Optional: Print loaded data for verification, but be careful with sensitive info
        # print(f"Loaded data: {data}")
