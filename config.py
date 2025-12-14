import os
from dotenv import load_dotenv
load_dotenv()
START_URL=os.getenv('START_URL','https://example.com')
MAX_PAGES=int(os.getenv('MAX_PAGES',50))
TIMEOUT=int(os.getenv('TIMEOUT',10))
