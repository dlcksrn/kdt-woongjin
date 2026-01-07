from supabase import create_client, Client
from config import Config

class SupabaseClient:
    """
    Supabase 데이터베이스와 상호작용하는 클라이언트
    """
    
    def __init__(self):
        self.url: str = Config.SUPABASE_URL
        self.key: str = Config.SUPABASE_KEY
        self.client: Client = create_client(self.url, self.key)
        
    def insert_positions(self, data_list: list):
        """
        API에서 수신한 데이터를 DB 스키마에 맞춰 변환 후 저장합니다.
        
        Args:
            data_list (list): API 원본 데이터 리스트
            
        Returns:
            bool: 저장 성공 여부
        """
        if not data_list:
            return False
            
        formatted_data = []
        
        for item in data_list:
            # 스키마 매핑
            record = {
                "line_id": item.get("subwayId"),
                "line_name": item.get("subwayNm"),
                "station_id": item.get("statnId"),
                "station_name": item.get("statnNm"),
                "train_number": item.get("trainNo"),
                "last_rec_date": item.get("lastRecptnDt"),
                "last_rec_time": item.get("recptnDt"),
                "direction_type": item.get("updnLine"),
                "dest_station_id": item.get("statnTid"),
                "dest_station_name": item.get("statnTnm"),
                "train_status": item.get("trainSttus"),
                "is_express": item.get("directAt"),
                "is_last_train": True if item.get("lstcarAt") == '1' else False
            }
            formatted_data.append(record)
            
        try:
            # bulk insert
            # v2.0.0+ 에서는 data, count = ... 형식이 아닐 수 있음. response.data 확인 필요.
            response = self.client.table("realtime_subway_positions").insert(formatted_data).execute()
            # 에러가 발생하지 않으면 성공으로 간주
            return True
        except Exception as e:
            print(f"[DB 저장 오류] {e}")
            return False
