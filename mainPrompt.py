import re
import datetime
import sys
from pathlib import Path
from fileCheck import verify_files
from query_edit import handle_query_and_display
from query_edit import handle_edit
from expense_income import expenditure
from expense_income import income
#주 프롬프트 :
SEPERATOR = '--------------------------------------------------------------'
SEPERATOR2 = '=============================================================='
LEDGER_FILE_SUFFIX = "_HL.txt"
HOME_DIR = Path.cwd()

#예산, 잔고기능 날짜 형식 검사
def get_valid_date(date_str):
    date_type = 0
    date_regex1 = re.compile(r'^(19[0-9]{2}|20[0-9]{2})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$')
    date_regex2 = re.compile(r'^(19[0-9]{2}|20[0-9]{2})-(0[1-9]|1[0-2])$')
    
    if date_regex1.match(date_str):
       date_type = 1
    elif date_regex2.match(date_str):
        date_type = 2
    if date_type == 0:
        raise ValueError("입력이 올바르지 않습니다.")
    
        
    # 2-2. 논리적 날짜 (예: 2월 30일) 및 미래 날짜 검사
    try:
        if date_type == 1: 
            date_d = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        elif date_type == 2:
            date_d = datetime.datetime.strptime(date_str, '%Y-%m').date()
        today = datetime.date.today()
        if date_d > today:
            # 미래 날짜
            raise ValueError
    except ValueError:
        # 존재하지 않는 날짜 (예: 2023-02-30)
        raise ValueError

    #형식이 유효하면
    return date_d, date_type

#잔고 기능 날짜 입력 형식 검사
def valid_balance_date(date_str):
    #문자열 앞 뒤 숫자인지 확인
    if not date_str or not date_str[0].isdecimal() or not date_str[-1].isdecimal() :
        print("입력이 올바르지 않습니다.")
        return -1
    date_arr = date_str.split()
    # 입력 유형에 따른 형식 검사
    try :
        # YYYY-MM
        if len(date_arr) == 1 :
            date_1, date_type = get_valid_date(date_arr[0])
            # 월의 마지막날로 설정
            if(date_1.month == 12) : date_2 = datetime.date(date_1.year+1,1,1)
            else : date_2 = datetime.date(date_1.year, date_1.month+1, 1)
            date_2 -= datetime.timedelta(days=1)
        # YYYY-MM-DD YYYY-MM-DD 혹은 YYYY-MM YYYY-MM
        elif len(date_arr) == 2 :
            date_1, date_type_1 = get_valid_date(date_arr[0])
            date_2, date_type_2 = get_valid_date(date_arr[1])
            # 서로 다른 형식 오류처리
            if date_type_1 != date_type_2 : 
                raise ValueError
            # 날짜 오름차순 정렬
            if date_1 > date_2 : 
                date_1, date_2 = date_2, date_1
            # 월의 마지막날로 설정
            if date_type_1 == 2:
                if(date_2.month == 12) : date_2 = datetime.date(date_2.year+1,1,1)
                else : date_2 = datetime.date(date_2.year, date_2.month+1, 1)
                date_2 -= datetime.timedelta(days=1)
        else : 
            raise ValueError
    except ValueError:
        print("입력이 올바르지 않습니다")
        return -1
    # 형식이 유효하면
    return date_1, date_2

#잔고 계산 및 출력
def calculate_balance(date_1, date_2, user_id):
    # 가계부 파일 열기
    ledger_file_name = str(user_id) + LEDGER_FILE_SUFFIX
    ledger_file_path = HOME_DIR / ledger_file_name
    try:
        with open(ledger_file_path, 'r', encoding='utf-8') as f:
            ledgers = [line for line in f if line]
    except Exception as e:
        print(f"!치명적오류: {ledger_file_name} 파일을 읽는 중 오류가 발생했습니다: {e}")
        print("프로그램을 종료시킵니다.")
        sys.exit()

    # 구간의 총 지출, 수입 계산
    total_expense = 0
    total_income = 0
    for ledger in ledgers:
        part = ledger.split('\t')
        date_str = part[0]
        date_d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_d >= date_1 and date_d <= date_2 :
            if part[1] == 'I':
                total_income += int(part[2])
            else :
                total_expense += int(part[2])
    # 잔고 출력
    period = str(date_1) + " ~ " + str(date_2)
    balance = total_income - total_expense
    print(SEPERATOR2)
    print(f"{'기간':<25} {'총 지출':>7} {'총 수입':>7} {'잔고':>7}")
    print(f"{period:<26} {total_expense:>10} {total_income:>10} {balance:>10}")
    print(SEPERATOR2)


#잔고 기능 메인 함수
def balance_menu(user_id):
    while True:
        date_str = input("기간을 입력하세요: ")
        date = valid_balance_date(date_str)
        if date != -1 : 
            break
        print(SEPERATOR)
    calculate_balance(date[0], date[1], user_id)

def print_mainPrompt():
    print('=주 프롬프트=\n')
    print('[지출] [수입] [조회] [편집] [검사]\n[잔고] [카테고리] [예산] [로그아웃]\n')
    choice = input("메뉴를 입력하세요: ")
    print(SEPERATOR)
    return choice

def callFunc(c, user_id):
    if(c == '지출'):
        expenditure(user_id)
        if(not verify_files()) : return -1
    elif(c == '수입'):
        income(user_id)
        if(not verify_files()) : return -1
    elif(c == '조회'):
        handle_query_and_display(user_id)
    elif(c == '편집'):
        handle_edit(user_id)
        if(not verify_files()) : return -1
    elif(c == '검사'):
        print("검사하는 중...")
        print(SEPERATOR)  
        if(verify_files()):
            print("성공적으로 검사되었습니다.\n주프롬프트로 돌아갑니다.")
            print(SEPERATOR2)
        else :  return -1
    elif(c == '잔고'):
        balance_menu(user_id)
    elif(c == '카테고리'):
        pass
    elif(c == '예산'):
        pass
    elif(c == '로그아웃'):
        return -1
        #로그아웃 함수(메인메뉴로 돌아감)
    

def mainPrompt(user_id):
    while(1):
        c = print_mainPrompt()
        check = callFunc(c, user_id)
        if check == -1: 
            return -1     


if __name__ == "__main__":
    mainPrompt("matthew")