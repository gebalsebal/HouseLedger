import sys
from mainPrompt import mainPrompt

USER_INFO_FILE = "user_info.txt"

def load_user_info(filename=USER_INFO_FILE):
    user_data = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                print(f"[디버그] {line_num}번째 줄 원본: {repr(line)}")
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',', 1)
                print(f"[디버그] split 결과: {parts}")
                if len(parts) != 2:
                    print(f"[경고] 잘못된 줄 형식: {line}")
                    continue
                user_id, password = parts
                user_data[user_id] = password
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        sys.exit()
    return user_data



def login(user_data):
    user_id = input("아이디 입력: ").strip()
    password = input("비밀번호 입력: ").strip()

    if user_id in user_data and user_data[user_id] == password:
        print("로그인 되었습니다.")
        mainPrompt(user_id)
        return True
    else:
        print("아이디 또는 비밀번호가 일치하지 않습니다.")
        return False

# 실행 예시
if __name__ == "__main__":
    users = load_user_info()
    login(users)