import random
from datetime import datetime

# 한양대 ERICA 캠퍼스 위치 목록
LOCATIONS = [
    "정문 앞",
    "학술정보관 앞",
    "제1공학관 앞",
    "제2공학관 앞",
    "학생복지관 앞",
    "기숙사 앞",
    "컨퍼런스홀 앞",
    "체육관 앞",
    "셔틀콕 앞",
]

# 이벤트 저장 리스트
event_log = []


# mock IMU 이벤트 생성 함수
def generate_mock_event():

    event = {
        # 이벤트 번호
        "event_id": len(event_log) + 1,

        # 발생 시간
        "timestamp": str(datetime.now()),

        # 이벤트 발생 위치
        "location": random.choice(LOCATIONS),

        # 기울기 값 (0~50도)
        "tilt": random.randint(0, 50),

        # 충격 감지 여부
        "shock": random.choice([True, False])
    }

    # 정상 / 이상 상태 판정
    event["status"] = (
        "abnormal"
        if event["tilt"] >= 30 or event["shock"]
        else "normal"
    )

    # 이벤트 저장
    event_log.append(event)

    return event


# 전체 이벤트 반환 함수
def get_events():
    return event_log


# 테스트 실행
if __name__ == "__main__":

    print(generate_mock_event())
    print(generate_mock_event())
    print(generate_mock_event())

    print("\n전체 이벤트:")
    print(get_events())