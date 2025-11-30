import os
import sys
import re
import datetime
from pathlib import Path
# 🥠2차: category 모듈 import
from category import SETTING_FILE_SUFFIX, get_payment_map

# --- 설정 변수 ---
# 홈 경로 설정
HOME_DIR = Path.cwd()
# 사용자 정보 파일 이름
USER_INFO_FILE = "user_info.txt"
# 가계부 파일 접미사
LEDGER_FILE_SUFFIX = "_HL.txt"
#CATEGORY_MAP = {
#    '식비': ['음식', '밥', 'food', '식'],
#    '교통': ['차', '지하철', 'transport', 'transportation', '교'],
#    '주거': ['월세', '관리비', 'housing', 'house', 'rent', '주'],
#    '여가': ['취미', '문화생활', 'hobby', 'leisure', '여'],
#    '입금': ['월급', '용돈', 'salary', 'wage', 'income', '입'],
#    '기타': ['etc', 'other', '기'],
#}

#PAYMENT_MAP = {
#    '현금': ['cash', '지폐', '현'],
#    '카드': ['card', 'credit', '카'],
#    '계좌이체': ['transfer', 'bank', 'account', '송금', '계'],
#}

SEPERATOR2 = '=============================================================='

def check_valid_category(category_input):
    # 🥠HL.txt에 기록된 카테고리(구분자)가 유효한 형식인지 검사.
    # 기존의 하드코딩된 CATEGORY_MAP을 사용X, 구분자 형식만 체크"""
    
    if not category_input:
        return False
        
    # 🥠C1, C12 같은 형식인지 체크
    if re.fullmatch(r'C[1-9][0-9]*', category_input):
        return True
    
    return False 

def check_valid_payment(payment_input):

    if not payment_input: # 빈 문자열은 항상 False
        return False
    payment_map = get_payment_map()
    
    for standard_name, synonyms in payment_map.items():
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
    id_list = []
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
        
        # 4. id 중복 검사
        user_id = user_id.lower()
        if user_id in id_list :
            return line_num
        id_list.append(user_id)

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
    #    - 1~999,999,999 (1~9자리, 0으로 시작 안 함) / 1차 수정
    amount_regex = re.compile(r'^([1-9][0-9]{0,8})$')

    sum = 0
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
        #### 카테고리 미구현 상태여서 주석 처리 
        # if not check_valid_category(category_str):
        #     return line_num

        # 6. Payment 검사 (외부 함수)
        if not check_valid_payment(payment_str.strip()):
            return line_num

        #7. 지출이 수입보다 큰 경우 검사를 위한 총 자산 계산
        if type_str == 'I' : 
            sum += int(amount_str) 
        else :
            sum -= int(amount_str)
        
    # 지출이 수입보다 큰 경우 검사
    if sum < 0 :
        return False
    # 모든 라인이 유효
    return None

# 🥠2차: check_setting_file 함수 구현 (설정 파일 문법/의미 규칙 검사)
def check_setting_file(settings_lines):
    
    category_set = set() # 표준명과 동의어 중복 검사
    is_category_section = True 
    found_separator = False 
    
    for i, line in enumerate(settings_lines, 1):
        line = line.strip()
        
        if not line:
            if is_category_section:
                is_category_section = False # 첫 번째 빈 줄 발견 (섹션 구분 시작)
                found_separator = True
            continue
        
        if is_category_section:
            # 1. 카테고리 형식 검사 (<구분자>\t<표준명>\t<동의어>...)
            parts = line.split('\t')
            if len(parts) < 2:
                return i 
            
            separator = parts[0]
            standard_name = parts[1].strip()
            synonyms = [p.strip() for p in parts[2:] if p.strip()] 

            # 2. 구분자 위치 및 형식 검사
            if separator != parts[0]: # <Category구분자> 앞 공백 검사
                 return i
            if not re.fullmatch(r'C[1-9][0-9]*', separator): # C1, C2 등 형식
                return i 
            
            # 3. 표준명/동의어 중복 검사 (의미 규칙)
            if standard_name in category_set or any(s in category_set for s in synonyms):
                return i 
            
            category_set.add(standard_name)
            for s in synonyms:
                category_set.add(s)

         #elif found_separator:
            # 4. 예산 섹션 검사 
            
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
    missing_setting_files_exist = False 
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
        
        # 🥠사용자 설정 파일 검사
        setting_file_name = f"{user_id}{SETTING_FILE_SUFFIX}"
        setting_file_path = HOME_DIR / setting_file_name
        if not setting_file_path.exists():
            if not missing_setting_files_exist:
                print("!오류: 설정 파일이 존재하지 않습니다.")
                print("!오류: 프로그램이 자동으로 새로운 파일을 생성 중 입니다.")
                missing_setting_files_exist = True
            # 파일이 없으면 빈 설정 파일 생성
            with open(setting_file_path, 'w', encoding='utf-8'): pass 
    
    if missing_ledger_files_exist or missing_setting_files_exist:
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
        if lineNum!=None and lineNum != False :
            print(f"!치명적오류: 현재 {ledger_file_name} {lineNum}행에서 오류가 발생되었습니다.")
            print("프로그램을 종료시킵니다.")
            sys.exit()
        elif lineNum == False :
            print(f"!치명적오류: 현재 {ledger_file_name}에서 지출이 수입보다 많습니다.")
            print("프로그램을 종료시킵니다.")
            sys.exit()
            
        # 🥠사용자 설정 파일 문법 검사 (치명적 오류)
        setting_file_name = f"{user_id}{SETTING_FILE_SUFFIX}"
        setting_file_path = HOME_DIR / setting_file_name
        
        if setting_file_path.stat().st_size == 0:
            continue
        
        try:
            with open(setting_file_path, 'r', encoding='utf-8') as f:
                settings_lines = f.readlines()
        except Exception as e:
            print(f"!치명적오류: {setting_file_name} 파일을 읽는 중 오류가 발생했습니다: {e}")
            print("프로그램을 종료시킵니다.")
            sys.exit()
        lineNum = check_setting_file(settings_lines)
        if lineNum is not None:
            # 치명적 오류 메시지 출력 후 종료
            print(f"!치명적오류: 현재 {setting_file_name} {lineNum}행에서 오류가 발생되었습니다.")
            print("프로그램을 종료시킵니다.")
            sys.exit()
            
    # 모든 검사를 통과하면 True 반환
    return True
