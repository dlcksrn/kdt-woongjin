import os
from dotenv import load_dotenv

# .env 파일 로드 (상위 디렉토리 탐색)
load_dotenv()

class Config:
    """
    환경 변수 및 설정 값을 관리하는 클래스
    """
    SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # 서울시 실시간 지하철 위치 API URL
    BASE_API_URL = "http://swopenAPI.seoul.go.kr/api/subway"
    
    @staticmethod
    def validate():
        """필수 환경 변수가 설정되어 있는지 확인"""
        if not Config.SEOUL_API_KEY:
            raise ValueError("SEOUL_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        if not Config.SUPABASE_URL:
            raise ValueError("SUPABASE_URL이 설정되지 않았습니다. .env 파일을 확인해주세요.")
        if not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
