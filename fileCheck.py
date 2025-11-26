import os
import sys
import re
import datetime
from pathlib import Path

# --- 설정 변수 ---
# 홈 경로 설정
HOME_DIR = Path.cwd()
# 사용자 정보 파일 이름
USER_INFO_FILE = "user_info.txt"
# 가계부 파일 접미사
LEDGER_FILE_SUFFIX = "_HL.txt"
CATEGORY_MAP = {
    '식비': ['음식', '밥', 'food', '식'],
    '교통': ['차', '지하철', 'transport', 'transportation', '교'],
    '주거': ['월세', '관리비', 'housing', 'house', 'rent', '주'],
    '여가': ['취미', '문화생활', 'hobby', 'leisure', '여'],
    '입금': ['월급', '용돈', 'salary', 'wage', 'income', '입'],
    '기타': ['etc', 'other', '기'],
}

PAYMENT_MAP = {
    '현금': ['cash', '지폐', '현'],
    '카드': ['card', 'credit', '카'],
    '계좌이체': ['transfer', 'bank', 'account', '송금', '계'],
}
SEPERATOR2 = '=============================================================='

def check_valid_category(category_input, type_str):
    if not category_input: # 빈 문자열은 항상 False
        return False
   
    if type_str == 'I':
        # 'I' (수입)인 경우, '입금' 카테고리만 검사
        standard_name = '입금'
        synonyms = CATEGORY_MAP.get(standard_name, []) 
        
        if standard_name == category_input:
            return True
        for s in synonyms:
            if s == category_input:
                return True
        # '입금' 및 동의어에 해당하지 않으면 False
        return False
    
    elif type_str == 'E':
        # 'E' (지출)인 경우, '입금'을 *제외한* 모든 카테고리 검사
        for standard_name, synonyms in CATEGORY_MAP.items():
            if standard_name == '입금':
                continue # 지출 검사 시 '입금'은 건너뜀
            
            if standard_name == category_input:
                return True
            for s in synonyms:
                if s == category_input:
                    return True
        # '입금' 외 다른 카테고리 및 동의어에 해당하지 않으면 False
        return False
    
    # type_str이 'I'나 'E'가 아닌 경우
    return False

def check_valid_payment(payment_input):

    if not payment_input: # 빈 문자열은 항상 False
        return False
    
    
    for standard_name, synonyms in PAYMENT_MAP.items():
        # 표준명 검사
        if standard_name == payment_input:
            return True
        # 동의어 검사
        for s in synonyms:
            if s == payment_input:
                return True
                
    # 일치하는 항목을 찾지 못하면 False 반환
    return False
            
def check_userfile(users):
    user_id_regex = re.compile(r'^[A-Za-z0-9]{6,12}$')
    password_regex = re.compile(r'^[A-Za-z0-9!@#$^&*]{8,15}$')

    # 1부터 시작하는 라인 번호와 함께 리스트를 순회합니다.
    for line_num, line in enumerate(users, 1):
        
        # 1. 형식 검사: 정확히 하나의 탭으로 분리되는지 확인
        parts = line.split('\t')
        if len(parts) != 2:
            # 탭이 없거나, 2개 이상이면 형식 오류
            return line_num
        
        user_id, password = parts[0], parts[1]

        # 2. ID 규칙 검사
        if not user_id_regex.match(user_id):
            return line_num

        # 3. Password 규칙 검사
        if not password_regex.match(password.strip()):
            return line_num

    # for 루프를 모두 통과했으면, 모든 라인이 유효합니다.
    return None

def check_ledgerfile(ledgers):
        
    today = datetime.date.today()
    # 1. Date 형식 Regex (1900-2099년, MM, DD 형식 체크)
    #    - 논리적 검사 (예: 2월 30일)는 strptime으로 별도 수행
    date_regex = re.compile(r'^(19[0-9]{2}|20[0-9]{2})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$')
    
    # 2. Type Regex
    type_regex = re.compile(r'^(E|I)$')
    
    # 3. Amount Regex
    #    - 1~9,999,999 (1~7자리, 0으로 시작 안 함)
    #    - 또는 10,000,000 (정확히 1천만)
    #    - ^([1-9][0-9]{0,6}|10000000)$
    amount_regex = re.compile(r'^([1-9][0-9]{0,6}|10000000)$')

    for line_num, line in enumerate(ledgers, 1):
        
        # 1. 형식 검사: 정확히 4개의 탭 (5개 필드)
        parts = line.split('\t')
        if len(parts) != 5:
            return line_num
        
        date_str, type_str, amount_str, category_str, payment_str = parts

        # 2. Date 검사
        # 2-1. 형식 (Regex)
        if not date_regex.match(date_str):
            return line_num
        
        # 2-2. 논리적 날짜 (예: 2월 30일) 및 미래 날짜 검사
        try:
            line_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            if line_date > today:
                # 미래 날짜
                return line_num
        except ValueError:
            # 존재하지 않는 날짜 (예: 2023-02-30)
            return line_num

        # 3. Type 검사
        if not type_regex.match(type_str):
            return line_num

        # 4. Amount 검사
        if not amount_regex.match(amount_str):
            # 형식 (선행 0, 기호) 또는 범위 (1천만 초과) 오류
            return line_num

        # 5. Category 검사 (외부 함수)
        if not check_valid_category(category_str, type_str):
            return line_num

        # 6. Payment 검사 (외부 함수)
        if not check_valid_payment(payment_str.strip()):
            return line_num

    # 모든 라인이 유효
    return None


#이 함수를 부른후 false면 프로그램 재시작
def verify_files():
    # 1. 사용자 파일(user_info.txt) 존재 확인
    user_file_path = HOME_DIR / USER_INFO_FILE

    if not user_file_path.exists():
        print("!오류: 현재 사용자 파일이 존재하지 않습니다.")
        print("!오류: 프로그램이 자동으로 새로운 파일을 생성 중 입니다.")
        # 새로운 빈 파일 생성
        user_file_path.touch()
        with open(user_file_path, "w", encoding='utf-8') as f:
            pass
        print("프로그램이 재시작됩니다.")
        print(SEPERATOR2)
        # 재시작을 위해 False 반환
        return False

    # 사용자 파일이 비어있는지 확인
    if user_file_path.stat().st_size == 0:
        # 파일은 있지만 내용이 없으면 통과 (새로 생성된 상태)
        return True
        
    # 2. 사용자 목록 읽기 및 가계부 파일 존재 확인
    try:
        with open(user_file_path, 'r', encoding='utf-8') as f:
            #2차 구현 strip
            users = [line for line in f]
    except Exception as e:
        # 파일을 읽는 도중 인코딩 등 다른 문제가 발생했을 경우
        print(f"!치명적오류: {USER_INFO_FILE} 파일을 읽는 중 오류가 발생했습니다: {e}")
        print("프로그램을 종료시킵니다.")
        sys.exit()
    
    # 3. 사용자 파일 문법 검사
    #    (예: 각 줄은 공백 없이 하나의 사용자 이름만 포함해야 함)
    lineNum = check_userfile(users)
    if(lineNum != None) :
        print(f"!치명적오류: 현재 {USER_INFO_FILE} {lineNum}행에서 오류가 발생되었습니다.")
        print("프로그램을 종료시킵니다.")
        sys.exit()


    missing_ledger_files_exist = False
    for line in users:
        parts = line.split('\t')     
        user_id = parts[0]
        ledger_file_name = f"{user_id}{LEDGER_FILE_SUFFIX}"
        ledger_file_path = HOME_DIR / ledger_file_name
        if not ledger_file_path.exists():
            if not missing_ledger_files_exist:
                print("!오류: 가계부 파일이 존재하지 않습니다.")
                print("!오류: 프로그램이 자동으로 새로운 파일을 생성 중 입니다.")
                missing_ledger_files_exist = True
            # 해당 사용자의 가계부 파일 생성
            with open(ledger_file_path, 'w', encoding='utf-8'): pass
    
    if missing_ledger_files_exist:
        print("프로그램이 재시작됩니다.")
        print(SEPERATOR2)
        # 재시작을 위해 False 반환
        return False

    # 4. 가계부 파일 문법 검사
    for line in users:
        parts = line.split('\t')     
        user_id = parts[0]
        ledger_file_name = f"{user_id}{LEDGER_FILE_SUFFIX}"
        ledger_file_path = HOME_DIR / ledger_file_name
        
        # 파일이 비어있으면 검사 통과
        if ledger_file_path.stat().st_size == 0:
            continue
            
        try:
            with open(ledger_file_path, 'r', encoding='utf-8') as f:
                #2차 구현 strip 
                ledgers = [line for line in f if line]
        except Exception as e:
            print(f"!치명적오류: {ledger_file_name} 파일을 읽는 중 오류가 발생했습니다: {e}")
            print("프로그램을 종료시킵니다.")
            sys.exit()
        lineNum = check_ledgerfile(ledgers)
        if(lineNum!=None) :
            print(f"!치명적오류: 현재 {ledger_file_name} {lineNum}행에서 오류가 발생되었습니다.")
            print("프로그램을 종료시킵니다.")
            sys.exit()
    # 모든 검사를 통과하면 True 반환
    return True
