import requests
import psycopg2
import time
import logging
from datetime import datetime
from config import API_KEY, DATABASE_URL, SUBWAY_LINES
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_realtime_position(line_name):
    """
    Fetch real-time train positions for a given subway line.
    """
    # URL Encoding for line name might be needed, but requests handles params well usually.
    # However, this API uses path parameters for some reason.
    # Format: http://swopenapi.seoul.go.kr/api/subway/{KEY}/{TYPE}/{SERVICE}/{START_INDEX}/{END_INDEX}/{subwayNm}
    
    # We use JSON as prefered type
    base_url = "http://swopenapi.seoul.go.kr/api/subway"
    url = f"{base_url}/{API_KEY}/json/realtimePosition/0/100/{line_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if 'realtimePositionList' in data:
            return data['realtimePositionList']
        else:
            if 'RESULT' in data and 'CODE' in data['RESULT']:
                 logger.warning(f"API Error for {line_name}: {data['RESULT']['CODE']} - {data['RESULT']['MESSAGE']}")
            return []
            
    except Exception as e:
        logger.error(f"Failed to fetch data for {line_name}: {e}")
        return []

def insert_data(conn, train_list):
    """
    Insert a list of train position dictionaries into the database.
    """
    if not train_list:
        return

    cursor = conn.cursor()
    query = """
        INSERT INTO realtime_train_positions (
            subway_line_id, subway_line_name, station_id, station_name,
            train_number, last_received_at, received_at, up_down_type,
            terminal_station_id, terminal_station_name, train_status,
            is_express, is_last_train
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s
        )
    """
    
    count = 0
    for train in train_list:
        try:
            # Map API fields to Schema params
            # Note: API dates are strings, Postgres adapts them usually, but safe to strict parse if needed.
            # API format example: "20231024123045" or similar? 
            # Description says: "최종수신날짜", "최종수신시간". 
            # Let's check the API spec more closely if possible or assume standard ISO or YYYYMMDD.
            # Based on common public data, it might need parsing. 
            # However, for now, we will pass them as is and let the driver/DB handle or fail if incompatible.
            # Safe approach: format if we see the format. 
            # Assuming 'recptnDt' is the main timestamp.
            
            # Helper to safely get int
            def get_int(val):
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return None

            # Helper to parse boolean
            def get_bool(val):
                return str(val) == '1'

            record = (
                train.get('subwayId'),
                train.get('subwayNm'),
                train.get('statnId'),
                train.get('statnNm'),
                train.get('trainNo'),
                train.get('lastRecptnDt'), # Date: YYYYMMDD
                train.get('recptnDt'),     # Time: YYYY-MM-DD HH:mm:ss (Usually) - Wait, let's verify format if we can.
                get_int(train.get('updnLine')),
                train.get('statnTid'),
                train.get('statnTnm'),
                get_int(train.get('trainSttus')),
                get_int(train.get('directAt')),
                get_bool(train.get('lstcarAt'))
            )
            cursor.execute(query, record)
            count += 1
        except Exception as e:
            logger.error(f"Failed to insert row for train {train.get('trainNo')}: {e}")
            conn.rollback() # Rollback the failed one, but maybe we want to continue?
            # For bulk insert, usually we do it in batch. For simplicity here, row by row with commit at end.
            
    conn.commit()
    cursor.close()
    logger.info(f"Inserted {count} records.")

def job():
    logger.info("Starting collection cycle...")
    
    # Connect to DB
    if not DATABASE_URL:
        logger.error("DATABASE_URL is not set. Skipping DB insertion.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.error(f"Could not connect to database: {e}")
        return

    total_records = 0
    for line in SUBWAY_LINES:
        logger.info(f"Fetching {line}...")
        data = fetch_realtime_position(line)
        if data:
            insert_data(conn, data)
            total_records += len(data)
        time.sleep(0.5) # Be gentle with the API
        
    conn.close()
    logger.info(f"Cycle finished. Total records: {total_records}")

if __name__ == "__main__":
    logger.info("Subway Collector Started")
    
    # Run once immediately
    job()
    
    # Schedule to run every 1 minute (or user preference)
    schedule.every(1).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
