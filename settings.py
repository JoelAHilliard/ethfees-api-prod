from pymongo import MongoClient
from dotenv import load_dotenv
import os 

load_dotenv()
MONGO_CLIENT_URL = os.getenv("MONGO_CLIENT_URL")
ETHER_SCAN_API_KEY = os.getenv("ETHER_SCAN_API_KEY")





client = MongoClient(MONGO_CLIENT_URL)
db = client