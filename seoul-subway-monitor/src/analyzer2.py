import pandas as pd
from data_loader import DataLoader

def run_analysis_2():
    """
    [분석 2] 지연 발생 구간 탐지 (Delay Hotspots)
    - 역별 체류 시간(도착~출발)을 추정하여 지연을 감지합니다.
    """
    print(">>> [분석 2] 지연 발생 구간(Hotspots) 탐지 시작...\n")
    
    loader = DataLoader()
    df = loader.fetch_data(limit=10000)
    
    if df.empty:
        return

    # 1. 데이터 소팅 (열차별, 시간순)
    df = df.sort_values(by=['train_number', 'created_at'])

    # 2. 체류 시간 추정 로직
    # 동일 열차(train_number), 동일 역(station_name)에서 관측된 '최초 시간'과 '최후 시간'의 차이를 체류 시간으로 근사
    # (API가 1분 등 주기적으로 호출되므로, 한 역에서 여러 번 찍히면 그 기간만큼 머문 것)
    
    # 관심 상태: 진입(0), 도착(1), 출발(2)
    # 사실상 역에 '있는' 동안을 봐야 하므로 0, 1 상태인 로그들을 묶습니다.
    staying_df = df[df['train_status'].isin(['0', '1', '2'])]
    
    if staying_df.empty:
        print("-> 분석할 열차 운행 데이터가 없습니다.")
        return

    # 그룹핑: 열차, 호선, 역
    dwell_stats = staying_df.groupby(['line_name', 'station_name', 'train_number']).agg(
        arrival_time=('created_at', 'min'),
        departure_time=('created_at', 'max'),
        log_count=('created_at', 'count')
    ).reset_index()

    dwell_stats['dwell_time_sec'] = (dwell_stats['departure_time'] - dwell_stats['arrival_time']).dt.total_seconds()

    # 3. 이상치 탐지 (예: 120초 이상 정차)
    # 주의: API 수집 주기가 60초라면, 1번 찍히면 0초, 2번 찍히면 60초 차이로 잡힘.
    # 따라서 dwell_time_sec가 0인 경우는 '잠깐 거쳐감' 혹은 '수집 주기 사이 통과'임.
    # 여기서는 'log_count'가 많은 경우를 오래 머문 것으로 간주하는 것이 더 정확할 수 있음.
    
    # 기준: 120초 이상 머무르고 있는 경우 (수집 주기에 따라 조정 필요)
    long_stop_df = dwell_stats[dwell_stats['dwell_time_sec'] >= 120].sort_values(by='dwell_time_sec', ascending=False)

    print(f"-> 총 {len(dwell_stats)}건의 역 정차 이력 분석")
    
    if not long_stop_df.empty:
        print(f"-> [주의] 장기 정차(지연 의심) 구간 발견 ({len(long_stop_df)}건)")
        # 보기 좋게 출력
        display_cols = ['line_name', 'station_name', 'train_number', 'dwell_time_sec', 'arrival_time']
        
        # 시간 포맷팅
        long_stop_df['arrival_time'] = long_stop_df['arrival_time'].dt.strftime('%H:%M:%S')
        
        print(long_stop_df[display_cols].head(20).to_string(index=False))
    else:
        print("-> 특이한 장기 정차(120초 이상) 구간이 발견되지 않았습니다.")

if __name__ == "__main__":
    run_analysis_2()
