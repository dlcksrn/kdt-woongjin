import os
from dotenv import load_dotenv

load_dotenv()

# Seoul Open Data API Key
API_KEY = os.getenv("SEOUL_API_KEY", "6e71466270636b733633654f6b4a7a")

# Supabase / Postgres Database URL
# Format: postgresql://[user]:[password]@[host]:[port]/[db]
DATABASE_URL = os.getenv("DATABASE_URL")

# List of Subway Lines to monitor
SUBWAY_LINES = [
    "1호선", "2호선", "3호선", "4호선", "5호선", 
    "6호선", "7호선", "8호선", "9호선", 
    "경의중앙선", "공항철도", "경춘선", 
    "수인분당선", "신분당선", "우이신설선"
]
