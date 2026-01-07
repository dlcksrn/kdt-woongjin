import pandas as pd
from db_client import SupabaseClient
from datetime import datetime
import time

class SubwayAnalyzer:
    """
    수집된 지하철 위치 데이터를 기반으로 모니터링 및 인사이트를 도출하는 분석 클래스
    """

    def __init__(self):
        self.db = SupabaseClient()

    def fetch_data_as_dataframe(self, days=1):
        """
        최근 n일 간의 데이터를 Supabase에서 가져와 Pandas DataFrame으로 반환합니다.
        """
        # 현재는 모든 데이터를 가져오는 단순한 쿼리 예시. 
        # 실제 운영 시에는 날짜 필터링(created_at)이 필요함.
        # Supabase API 한계(default 1000 row)가 있으므로, 필요 시 페이지네이션 구현 필요.
        # 여기서는 최근 1000개 데이터만 샘플링하여 분석한다고 가정.
        
        try:
            response = self.db.client.table("realtime_subway_positions") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(2000) \
                .execute()
            
            data = response.data
            if not data:
                print("[분석 경고] 분석할 데이터가 없습니다.")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            
            # 날짜 컬럼 타입 변환
            df['created_at'] = pd.to_datetime(df['created_at'])
            if 'last_rec_time' in df.columns:
                # API 원본 포맷에 따라 파싱 포맷 조정 필요할 수 있음
                # 예: 20240101120000 -> 포맷팅 필요. 여기서는 그대로 둠.
                pass
                
            return df
        except Exception as e:
            print(f"[데이터 로드 오류] {e}")
            return pd.DataFrame()

    def analyze_interval_regularity(self, df: pd.DataFrame, station_name: str, line_id: str):
        """
        1. 배차 간격 정기성 분석
        특정 역(station_name)의 특정 호선(line_id)에 도착한 열차들의 시간 간격을 분석합니다.
        """
        if df.empty:
            return

        # 필터링: 특정 노선, 데이터가 특정 역에 있는 경우(train_status=1 도착 or 0 진입)
        # statnId 나 statnNm 사용
        target_df = df[
            (df['line_id'] == line_id) & 
            (df['station_name'] == station_name) &
            (df['train_status'].isin(['0', '1'])) # 0:진입, 1:도착
        ].copy()
        
        if target_df.empty:
            print(f"[{station_name}] 해당 역의 도착 데이터가 없습니다.")
            return

        # 시간순 정렬
        target_df = target_df.sort_values(by='created_at')
        
        # 앞 열차와의 시간 차이(초) 계산
        target_df['prev_arrival'] = target_df['created_at'].shift(1)
        target_df['interval_sec'] = (target_df['created_at'] - target_df['prev_arrival']).dt.total_seconds()
        
        # 결과 출력
        print(f"\n=== [{station_name}] 배차 간격 분석 ===")
        print(target_df[['created_at', 'train_number', 'interval_sec']].dropna().tail(10))
        
        avg_interval = target_df['interval_sec'].mean()
        max_interval = target_df['interval_sec'].max()
        print(f"-> 평균 간격: {avg_interval:.1f}초, 최대 간격: {max_interval:.1f}초")

    def analyze_delay_hotspots(self, df: pd.DataFrame):
        """
        2. 지연 발생 구간 탐지 (체류 시간 분석)
        동일 열차(train_number)가 동일 역(station_name)에서 '도착(1)' 상태에서 '출발(2)' 상태로 바뀌는 시간 차이 측정
        """
        if df.empty:
            return
            
        # 열차번호와 역이 같은 그룹 내에서 상태 변화를 추적
        # 데이터가 충분히 쌓여야 분석 가능하므로 로직만 구현
        
        print(f"\n=== 지연 발생 구간 탐지 (체류 시간) ===")
        # 간략화: 가장 최근 데이터 기준 각 열차의 수신 시간 간격 확인 (오랫동안 업데이트 없는 열차)
        
        current_time = pd.Timestamp.now(tz='UTC') # Supabase는 UTC 기준일 가능성 높음
        
        # 각 열차별 마지막 수신 시간
        last_seen = df.groupby(['train_number', 'line_name'])['created_at'].max().reset_index()
        last_seen['seconds_since_update'] = (current_time - last_seen['created_at']).dt.total_seconds()
        
        # 300초(5분) 이상 업데이트 없는 열차 (통신 장애 혹은 장기 정차)
        delayed_trains = last_seen[last_seen['seconds_since_update'] > 300]
        
        if not delayed_trains.empty:
            print(f"-> 장기 미수신/정차 의심 열차 {len(delayed_trains)}대 발견")
            print(delayed_trains)
        else:
            print("-> 특이 사항 없음 (모든 열차가 최근 5분 내 통신됨)")

    def run_full_report(self):
        """
        전체 분석 리포트 실행
        """
        print(">>> 데이터 분석 리포트 생성 중...")
        df = self.fetch_data_as_dataframe()
        
        if df.empty:
            return
            
        print(f"-> 총 {len(df)}건의 데이터를 로드했습니다.")
        
        # 예시 분석 실행
        # 2호선 성수역 예시
        self.analyze_interval_regularity(df, station_name="성수", line_id="1002") # 1002는 2호선 ID
        
        self.analyze_delay_hotspots(df)
        
        print("\n>>> 분석 완료.")

if __name__ == "__main__":
    analyzer = SubwayAnalyzer()
    analyzer.run_full_report()
