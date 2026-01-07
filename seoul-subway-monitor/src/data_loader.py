import pandas as pd
from db_client import SupabaseClient

class DataLoader:
    """
    데이터 분석을 위한 공통 데이터 로더
    """
    def __init__(self):
        self.db = SupabaseClient()

    def fetch_data(self, limit=5000):
        """
        Supabase에서 최신 데이터를 가져와 DataFrame으로 반환
        """
        try:
            # 데이터가 많아질 경우를 대비해 limit을 적절히 조정
            response = self.db.client.table("realtime_subway_positions") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            data = response.data
            if not data:
                print("[데이터 로드 경고] 데이터가 없습니다. main.py를 실행하여 데이터를 먼저 수집해주세요.")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            
            # 시간 컬럼 변환
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # 분석에 필요한 경우 숫자형 변환
            # df['station_id'] = pd.to_numeric(df['station_id'], errors='coerce')
            
            return df
        except Exception as e:
            print(f"[데이터 로드 오류] {e}")
            return pd.DataFrame()
