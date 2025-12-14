import os
from dotenv import load_dotenv

load_dotenv()

CRAWLER = {
    'START_URL': os.getenv('START_URL', 'https://example.com'),
    'MAX_PAGES': int(os.getenv('MAX_PAGES', 50)),
    'TIMEOUT': int(os.getenv('TIMEOUT', 10)),
    'BATCH_SIZE': int(os.getenv('BATCH_SIZE', 5)),
}

LOGGING = {
    'LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
