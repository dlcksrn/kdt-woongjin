import pandas as pd
from data_loader import DataLoader
import sys

def run_analysis_1():
    """
    [분석 1] 배차 간격 정기성 분석 (Interval Regularity)
    - 모든 역에 대해 도착 열차 간의 시간 간격을 계산합니다.
    - 배차 간격의 평균, 표준편차, 최대값을 표 형태로 출력합니다.
    """
    print(">>> [분석 1] 전 역사 배차 간격 분석 시작...\n")
    
    loader = DataLoader()
    df = loader.fetch_data(limit=10000)
    
    if df.empty:
        return

    # 1. 도착(1) 또는 진입(0) 데이터만 필터링 (역에 있는 상태)
    # 분석 정확도를 위해 '도착(1)' 상태를 기준으로 잡는 것이 가장 좋음
    target_df = df[df['train_status'] == '1'].copy()
    
    if target_df.empty:
        print("-> 분석할 '도착' 데이터가 부족합니다. (데이터 수집이 더 필요합니다)")
        return

    # 2. 필요한 컬럼만 추출 및 정렬
    # 그룹화 기준: 호선, 역명, 상/하행 구분
    target_df = target_df.sort_values(by=['line_name', 'station_name', 'direction_type', 'created_at'])

    # 3. 배차 간격 계산
    # 그룹별로 이전 열차 도착 시간과의 차이를 구함
    target_df['prev_arrival'] = target_df.groupby(['line_name', 'station_name', 'direction_type'])['created_at'].shift(1)
    target_df['interval_sec'] = (target_df['created_at'] - target_df['prev_arrival']).dt.total_seconds()

    # 4. 결측치 제거 (각 그룹의 첫 번째 열차는 간격 계산 불가하므로 제외)
    valid_intervals = target_df.dropna(subset=['interval_sec'])

    if valid_intervals.empty:
        print("-> 배차 간격을 계산할 수 없습니다. (역별로 최소 2대 이상의 열차가 도착해야 합니다)")
        return

    # 5. 통계 집계 (평균, 최대, 표준편차)
    stats = valid_intervals.groupby(['line_name', 'direction_type', 'station_name'])['interval_sec'].agg(['count', 'mean', 'max', 'std']).reset_index()
    
    # 6. 보기 좋게 포맷팅
    stats['mean'] = stats['mean'].round(1)
    stats['max'] = stats['max'].round(1)
    stats['std'] = stats['std'].round(1).fillna(0) # 데이터가 적어 std가 NaN이면 0으로 처리
    
    # 상행/하행 코드 변환 (0:상행/내선, 1:하행/외선)
    stats['direction_desc'] = stats['direction_type'].apply(lambda x: '상행/내선' if str(x) == '0' else '하행/외선')

    # 컬럼 이름 변경
    stats = stats.rename(columns={
        'line_name': '호선',
        'station_name': '역명',
        'direction_desc': '방향',
        'count': '관측수',
        'mean': '평균간격(초)',
        'max': '최대간격(초)',
        'std': '변동성(표준편차)'
    })

    # 출력할 컬럼 순서 정리
    output_columns = ['호선', '역명', '방향', '평균간격(초)', '최대간격(초)', '변동성(표준편차)', '관측수']
    final_table = stats[output_columns].sort_values(by=['호선', '역명'])

    # 7. 표 출력
    print(final_table.to_string(index=False))
    print(f"\n[요약] 총 {len(final_table)}개 구간(역/방향) 분석 완료.")
    
    # (선택) CSV 파일로 저장
    # final_table.to_csv("analysis_result_1.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    run_analysis_1()
