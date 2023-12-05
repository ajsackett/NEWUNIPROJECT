from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

def configure():
    load_dotenv()

configure()

url = os.getenv('db_connection_url')

def create_db_engine():
    engine = create_engine(
        url=url,
        connect_args={
            'ssl': {
                'ca': r'cacert.pem' # Use 'r' for raw string
                # Add other SSL options if needed, such as 'cert' and 'key'
            }
        }
    )
    return engine

engine = create_db_engine()



