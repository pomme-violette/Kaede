import os
from dotenv import load_dotenv

load_dotenv(verbose=True, dotenv_path='.env')

BASE_URI = os.environ.get('BASE_URI')
EXPORT_DIR = os.environ.get('EXPORT_DIR')
COOKIE_ROOTDIR = os.environ.get('COOKIE_ROOTDIR')
COOKIES = os.environ.get('COOKIES')
EXPORT_CONTENT_HEADER = os.environ.get('EXPORT_CONTENT_HEADER')
COPYRIGHT = os.environ.get('COPYRIGHT')