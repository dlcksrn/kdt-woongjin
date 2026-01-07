import requests
import json
from config import Config

class SeoulSubwayAPI:
    """
    서울시 열차 위치 정보를 가져오는 API 클라이언트
    """
    
    def __init__(self):
        self.api_key = Config.SEOUL_API_KEY
        self.base_url = Config.BASE_API_URL

    def get_realtime_positions(self, line_name: str):
        """
        특정 호선의 실시간 열차 위치 정보를 조회합니다.
        
        Args:
            line_name (str): 조회할 호선명 (예: '1호선', '2호선')
            
        Returns:
            list: 열차 위치 정보 리스트 (실패 시 빈 리스트 반환)
        """
        # API 키 인코딩 처리 등이 필요할 수 있으나, 일반적으로 raw string 사용
        # URL 패턴: /api/subway/{KEY}/json/realtimePosition/0/100/{LINE_NAME}
        url = f"{self.base_url}/{self.api_key}/json/realtimePosition/0/100/{line_name}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if 'realtimePositionList' in data:
                return data['realtimePositionList']
            else:
                if 'errorMessage' in data:
                    print(f"[API 오류] {data['errorMessage'].get('message', '알 수 없는 오류')} (Line: {line_name})")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"[HTTP 요청 오류] {e}")
            return []
        except json.JSONDecodeError:
            print(f"[JSON 파싱 오류] 응답을 분석할 수 없습니다.")
            return []
        except Exception as e:
            print(f"[예상치 못한 오류] {e}")
            return []
