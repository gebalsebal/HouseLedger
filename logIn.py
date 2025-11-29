import sys
import os
import re
from mainPrompt import mainPrompt
# 🥠2차: category 모듈 import
from category import create_default_settings, load_user_categories

USER_INFO_FILE = "user_info.txt"
SETTING_FILE_SUFFIX = "_setting.txt" # 🥠2차: setting 파일
SEPERATOR2 = '=============================================================='

##회원가입 파트

def load_user_info(filename=USER_INFO_FILE):
    user_data = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                #print(f"[디버그] {line_num}번째 줄 원본: {repr(line)}")
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t', 1)
                #print(f"[디버그] split 결과: {parts}")
                if len(parts) != 2:
                    #print(f"[경고] 잘못된 줄 형식: {line}")
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
        print(SEPERATOR2)
        mainPrompt(user_id)
        return True
    else:
        print("아이디 또는 비밀번호가 일치하지 않습니다.")
        return False

##로그인 파트

# 아이디 유효성 검사: 6~12자, 영문+숫자만 허용
def is_valid_id(user_id):
    return bool(re.fullmatch(r'[A-Za-z0-9]{6,12}', user_id))

# 비밀번호 유효성 검사: 8~15자, 영문+숫자+특수문자(!@#$^&*)만 허용
def is_valid_password(password):
    return bool(re.fullmatch(r'[A-Za-z0-9!@#$^&*]{8,15}', password))

def signup():
    print("\n[회원가입 메뉴]")
    print("----------------------------------------------")
    user_id = input("아이디 입력: ").strip()
    password = input("비밀번호 입력: ").strip()
    password_check = input("비밀번호 확인: ").strip()

    # 디버그 출력
    # print(f"[디버그] 입력된 아이디: {repr(user_id)}")
    # print(f"[디버그] 입력된 비밀번호: {repr(password)}")
    # print(f"[디버그] 아이디 유효성 검사 결과: {is_valid_id(user_id)}")
    # print(f"[디버그] 비밀번호 유효성 검사 결과: {is_valid_password(password)}")

    # 유효성 검사
    if not is_valid_id(user_id):
        print("아이디는 6~12자의 영문 대소문자와 숫자만 사용할 수 있습니다.\n")
        return
    if not is_valid_password(password):
        print("비밀번호는 8~15자의 영문, 숫자, 특수문자(!@#$^&*)만 사용할 수 있습니다.\n")
        return
    if password != password_check:
        print("비밀번호가 일치하지 않습니다. 다시 시도해주세요.\n")
        return

    # 파일이 없으면 새로 생성
    if not os.path.exists(USER_INFO_FILE):
        open(USER_INFO_FILE, "w", encoding="utf-8").close()

    # 아이디 중복 체크
    with open(USER_INFO_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            existing_id = line.split('\t', 1)[0]
            if existing_id == user_id:
                print("이미 사용 중인 아이디입니다. 다른 아이디를 입력해주세요.\n")
                return

    # 사용자 정보 저장 (탭 문자로 구분)
    with open(USER_INFO_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user_id}\t{password}\n")

    # 개인 장부 파일 생성
    ledger_filename = f"{user_id}_HL.txt"
    open(ledger_filename, "a", encoding="utf-8").close()
    
    # 🥠2차: setting 파일 생성
    settings_success = create_default_settings(user_id)
    settings_filename = f"{user_id}{SETTING_FILE_SUFFIX}"

    print(f"회원가입이 완료되었습니다. 장부 파일 '{ledger_filename}' 및 설정 파일 '{settings_filename}'이 생성되었습니다.")
    print("----------------------------------------------\n")

if __name__ == "__main__":
    signup()