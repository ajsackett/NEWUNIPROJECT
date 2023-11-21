import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
def configure():
    load_dotenv()

configure()

def configure():
    load_dotenv()

configure()

url = os.getenv('db_connection_url')



engine = create_engine(
    url =url,
    connect_args={
        'ssl': {
            'ssl_ca': '/etc/ssl/cert.pem'
        }
    }

)



#first_result_2dict = first_result._asdict()
#print(first_result_2dict)
#print(type(first_result_2dict))
