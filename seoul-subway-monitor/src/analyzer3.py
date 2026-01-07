import pandas as pd
from data_loader import DataLoader

def run_analysis_3():
    """
    [분석 3] 회차 효율성 분석 (Turnaround Efficiency)
    - 종착역 도착 후 다시 시발역에서 운행 시작할 때까지 걸린 시간 분석
    """
    print(">>> [분석 3] 회차 효율성(Turnaround) 분석 시작...\n")
    
    loader = DataLoader()
    df = loader.fetch_data(limit=15000)
    
    if df.empty:
        return
        
    # 1. 종착역 도착 데이터 찾기
    # train_status: 1(도착), 그리고 현재 역이 종착역(dest_station_name)과 같을 때?
    # 혹은 단순히 어떤 열차번호가 방향(updnLine)을 바꾼 시점을 찾음.
    
    # 열차별 시간순 정렬
    df = df.sort_values(by=['train_number', 'created_at'])
    
    analyzed_data = []
    
    # 열차별로 그룹
    for train_no, train_df in df.groupby('train_number'):
        # 방향(direction_type)이 바뀌는 지점 탐지
        # 예: 0(상행) -> 1(하행) 혹은 그 반대
        train_df['prev_dir'] = train_df['direction_type'].shift(1)
        
        # 방향이 달라진 행 추출 (첫 행 제외)
        turnaround_points = train_df[
            (train_df['prev_dir'].notnull()) & 
            (train_df['direction_type'] != train_df['prev_dir'])
        ]
        
        for idx, row in turnaround_points.iterrows():
            # 방향이 바뀌기 직전의 마지막 로그(회차 전 도착) 시간을 찾아야 함
            # turnaround_points의 행은 '회차 후 출발(혹은 대기)' 상태임
            
            # 직전 로그 찾기 (index 활용)
            # 전체 train_df에서 현재 idx보다 작은 인덱스 중 가장 큰 것
            prev_logs = train_df.loc[:idx-1]
            if prev_logs.empty:
                continue
                
            last_arrival = prev_logs.iloc[-1]
            
            # 회차 시간 = (새 방향 감지 시간) - (이전 방향 마지막 기록 시간)
            turnaround_time = (row['created_at'] - last_arrival['created_at']).total_seconds()
            
            analyzed_data.append({
                'line_name': row['line_name'],
                'train_number': train_no,
                'station_name': row['station_name'], # 회차 역
                'prev_direction': last_arrival['direction_type'],
                'new_direction': row['direction_type'],
                'turnaround_time_sec': turnaround_time,
                'detected_at': row['created_at']
            })
            
    if not analyzed_data:
        print("-> 회차 이벤트가 감지되지 않았습니다. (데이터가 더 누적되어야 합니다)")
        return
        
    result_df = pd.DataFrame(analyzed_data)
    
    # 이상치 필터링 (너무 긴 시간은 회차가 아니라 운행 종료 후 재투입일 수 있음. 30분 이내만 회차로 간주)
    result_df = result_df[result_df['turnaround_time_sec'] < 1800]
    
    print(f"-> 총 {len(result_df)}건의 회차 감지")
    
    if not result_df.empty:
        # 보기 좋게 포맷팅
        display_df = result_df[['line_name', 'station_name', 'train_number', 'turnaround_time_sec', 'detected_at']].copy()
        display_df['turnaround_time_sec'] = display_df['turnaround_time_sec'].round(1)
        
        print(display_df.to_string(index=False))
        
        # 역별 평균 회차 시간
        avg_turnaround = result_df.groupby('station_name')['turnaround_time_sec'].mean().reset_index()
        print("\n[역별 평균 회차 소요시간]")
        print(avg_turnaround.to_string(index=False))

if __name__ == "__main__":
    run_analysis_3()
