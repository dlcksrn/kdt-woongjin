import time
import schedule
import sys
import os

# 현재 디렉토리(src)를 path에 추가하여 모듈 import 원활하게 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from api_client import SeoulSubwayAPI
from db_client import SupabaseClient

def job():
    """
    주기적으로 실행될 작업
    """
    print("[작업 시작] 데이터 수집 및 저장 시도...")
    
    api = SeoulSubwayAPI()
    db = SupabaseClient()
    
    # 수집할 호선 목록 (서울시 공공데이터 포털 기준 정의된 호선명)
    target_lines = ["1호선", "2호선", "3호선", "4호선", "5호선", "6호선", "7호선", "8호선", "9호선"]
    
    total_inserted = 0
    
    for line in target_lines:
        print(f" - {line} 데이터 조회 중...")
        data = api.get_realtime_positions(line)
        
        if data:
            if db.insert_positions(data):
                print(f"   -> {len(data)}건 저장 완료.")
                total_inserted += len(data)
            else:
                print(f"   -> 저장 실패.")
        else:
            print(f"   -> 데이터 없음 (운행 시간이 아닐 수 있음).")
            
    print(f"[작업 종료] 총 {total_inserted}건 처리됨.\n")

def main():
    """
    메인 실행 함수
    """
    try:
        Config.validate()
    except ValueError as e:
        print(f"[설정 오류] {e}")
        return

    print("=== 서울 지하철 실시간 위치 모니터링 시스템 ===")
    print("스케줄러 시작: 1분마다 실행됩니다. (종료: Ctrl+C)")
    
    # 프로그램 시작 시 1회 즉시 실행
    job()
    
    # 1분마다 실행
    schedule.every(1).minutes.do(job)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[시스템 종료] 사용자 요청에 의해 종료합니다.")

if __name__ == "__main__":
    main()
