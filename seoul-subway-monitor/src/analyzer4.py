import pandas as pd
from data_loader import DataLoader

def run_analysis_4():
    """
    [분석 4] 급행/일반 열차 간섭 분석 (Congestion/Overtake)
    - 9호선 등 급행 운영 노선에서 앞선 완행 열차와의 간격이 좁아지는지 분석
    """
    print(">>> [분석 4] 급행/일반 열차 간섭 분석 시작...\n")
    
    loader = DataLoader()
    # is_express 컬럼 활용 (1:급행, 0:일반)
    df = loader.fetch_data(limit=5000)
    
    if df.empty:
        return
    
    # 급행 데이터가 있는 노선만 필터링 (주로 9호선, 1호선 일부 등)
    # is_express가 1인 데이터가 있는지 확인
    # API 데이터에서 문자열 '1'일 수도 있고 숫자 1일 수도 있음
    has_express = df[df['is_express'].astype(str).isin(['1', 'True'])]
    
    if has_express.empty:
        print("-> 급행 열차 데이터가 발견되지 않았습니다. (현재 시간대에 급행이 없거나, 지원하지 않는 호선일 수 있습니다)")
        return
    
    target_lines = has_express['line_name'].unique()
    print(f"-> 급행 운행 노선 발견: {target_lines}")
    
    # 9호선을 타겟으로 예시 분석
    # 같은 노선, 같은 방향, 인접한 시간대의 급행(Express)과 일반(Local) 열차 간의 거리(역 차이 혹은 시간 차이) 계산
    
    # 이번에는 간단하게 '역' 단위가 아닌 '도착 시간' 기준으로
    # 특정 역에 급행이 도착했을 때, 직전 일반 열차가 언제 도착했는지(Headway) 비교
    
    report_data = []

    for line in target_lines:
        line_df = df[df['line_name'] == line].sort_values(['station_name', 'direction_type', 'created_at'])
        
        # 역별로 그룹핑
        for (station, direction), group in line_df.groupby(['station_name', 'direction_type']):
            # 도착(1) 데이터만 
            arrivals = group[group['train_status'] == '1'].sort_values('created_at')
            
            # 각 급행 열차에 대해 바로 앞의 일반 열차 찾기
            express_trains = arrivals[arrivals['is_express'].astype(str).isin(['1', 'True'])]
            local_trains = arrivals[arrivals['is_express'].astype(str).isin(['0', 'False'])]
            
            if express_trains.empty or local_trains.empty:
                continue
                
            for _, exp_row in express_trains.iterrows():
                # 해당 급행 열차 도착 시간보다 이전에 도착한 일반 열차 중 가장 최근 것
                prev_locals = local_trains[local_trains['created_at'] < exp_row['created_at']]
                
                if not prev_locals.empty:
                    last_local = prev_locals.iloc[-1]
                    time_diff = (exp_row['created_at'] - last_local['created_at']).total_seconds()
                    
                    # 간격이 너무 좁으면(예: 2분 미만) 간섭/추월 직전으로 간주
                    status = "정상"
                    if time_diff < 120: 
                        status = "간섭주의(근접)"
                    
                    report_data.append({
                        'line': line,
                        'station': station,
                        'direction': direction, # 0:상행, 1:하행
                        'express_train': exp_row['train_number'],
                        'local_train': last_local['train_number'],
                        'headway_sec': time_diff,
                        'status': status,
                        'time': exp_row['created_at']
                    })
    
    if not report_data:
        print("-> 분석할 급행/일반 교차 데이터가 충분하지 않습니다.")
        return

    result = pd.DataFrame(report_data)
    
    # 간섭 주의 구간만 필터링해서 보여주거나, 전체 요약
    print(f"-> 총 {len(result)}건의 급행/일반 간격 데이터 분석")
    
    hotspots = result[result['status'] == "간섭주의(근접)"]
    if not hotspots.empty:
        print("\n[주의] 급행-일반 간격 협소 구간 (간섭 예상):")
        print(hotspots[['line', 'station', 'direction', 'headway_sec', 'status']].to_string(index=False))
    else:
        print("\n-> 급행과 일반 열차 간의 위험한 근접(간섭)은 발견되지 않았습니다. (모두 2분 이상 간격 유지 중)")

if __name__ == "__main__":
    run_analysis_4()
