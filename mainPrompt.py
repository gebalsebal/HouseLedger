import re
import datetime
import sys
from pathlib import Path
from fileCheck import verify_files
from query_edit import handle_query_and_display
from query_edit import handle_edit
from query_edit import get_valid_amount
from expense_income import expenditure
from expense_income import income

import category


#주 프롬프트 :
SEPERATOR = '--------------------------------------------------------------'
SEPERATOR2 = '=============================================================='
LEDGER_FILE_SUFFIX = "_HL.txt"
SETTING_FILE_SUFFIX = "_setting.txt"
HOME_DIR = Path.cwd()
user_id_global = ""

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
    # 검색 결과 없을때
    if total_expense == 0 and total_income == 0 :
        print("검색 결과가 없습니다.")
        return
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
    print(SEPERATOR2)

def valid_budget_date(date_str):
    """
    YYYY-MM 형식 검사
    """
    try:
        date_d, date_type = get_valid_date(date_str)
        if date_type != 2:
            print("예산 날짜는 YYYY-MM 형식이어야 합니다.")
            return False
            
        return True
    except ValueError:
        print("예산 날짜는 YYYY-MM 형식이여야 합니다.")
        return False

def valid_budget_amount(amount_str):
    """
    예산 금액 형식 검사
    """
    try:
        get_valid_amount(amount_str)
        return True
    except ValueError as e:
        print(e)
        return False

def calculate_budget(date_str=None):
    """
    예산 및 지출 비교 계산 출력
    """
    setting_file_name =user_id_global + SETTING_FILE_SUFFIX
    setting_file_path = HOME_DIR / setting_file_name
    ledger_file_name =user_id_global + LEDGER_FILE_SUFFIX
    ledger_file_path = HOME_DIR / ledger_file_name
    
    budgets = {} # { 'YYYY-MM': amount }
    is_budget_section = False
    # 1. 예산 파일 읽기
    try:
        if setting_file_path.exists():
            with open(setting_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    #카테고리 내용 건너뛰기
                    if line == '\n' : 
                        is_budget_section = True
                        continue
                    if not is_budget_section : continue
                    parts = line.split('\t')                    
                    b_date = parts[0]
                    b_amount = int(parts[1])
                    # date_str 인자가 있으면 해당 날짜만 로드
                    if date_str is None :
                        budgets[b_date] = b_amount
            if date_str:
                budgets[date_str] = 0
                
        else:
            # 설정 파일이 없으면 빈 상태로 진행
            print(f"!오류: 가계부 파일이 존재하지 않습니다. 새로운 파일 생성.")
            with open(setting_file_path, 'w', encoding='utf-8') as f:
                pass
    except Exception as e:
        print(f"!오류: {setting_file_name} 파일을 읽는 중 오류가 발생했습니다: {e}")
        return False

    if not budgets and not date_str:
        print("조회할 예산내역이 없습니다.")
        return False # 오류는 아니므로 True

    # 2. 가계부 파일 읽기 및 지출 합산
    expenses = {key: 0 for key in budgets.keys()} # { 'YYYY-MM': total_expense }
    
    try:
        if ledger_file_path.exists():
            with open(ledger_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.split('\t')
                    # parts: [Date, Type, Amount, Category, Payment]
                    l_date_str = parts[0] # YYYY-MM-DD
                    l_type = parts[1]
                    l_amount = int(parts[2])

                    # YYYY-MM 추출
                    l_month_str = l_date_str[:7]

                    # 해당 월이 예산 목록에 있고, 지출(E)인 경우 합산
                    # (설계서 잔고 부분 참고: 수입(I) 제외한 것이 지출)
                    if l_month_str in expenses and l_type == 'E':
                        expenses[l_month_str] += l_amount
    except Exception as e:
        print(f"!오류: {ledger_file_path} 파일을 읽는 중 오류가 발생했습니다: {e}")
        return False

    # date_str이 None이 아닌경우 처리
    if date_str :
        return expenses[date_str]
    
    # 날짜순 정렬하여 출력
    sorted_months = sorted(budgets.keys())
    for month in sorted_months:
        b_amt = budgets[month]
        e_amt = expenses[month]
        diff = b_amt - e_amt
        b_str = "초과 금액 " if diff < 0  else "예산 차액"
        print(f"{month:<8} 예산 금액:{b_amt:>10} / {b_str}:{diff:>10}")
    print('\n')

    return True

def check_file_date(date_str):
    """
    설정 파일에 해당 날짜가 존재하는지 확인
    """
    setting_file_name = user_id_global + SETTING_FILE_SUFFIX
    setting_file_path = HOME_DIR / setting_file_name
    is_budget_section = False
    
    if not setting_file_path.exists():
        print(f"!오류: 가계부 파일이 존재하지 않습니다. 새로운 파일 생성.")
        with open(setting_file_path, 'w', encoding='utf-8') as f:
            pass
        return False
        
    try:
        with open(setting_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                #카테고리 내용 건너뛰기
                if line == '\n' : 
                    is_budget_section = True
                    continue
                if not is_budget_section : continue

                parts = line.split('\t')
                if parts[0] == date_str:
                    return True
    except Exception as e:
        print(e)
        return False
    
    return False

def append_budget_file(date_str, amount):
    """
    설정 파일에 예산 추가
    """
    setting_file_name = user_id_global + SETTING_FILE_SUFFIX
    setting_file_path = HOME_DIR / setting_file_name
    
    try:
        with open(setting_file_path, 'a', encoding='utf-8') as f:
            f.write(f"{date_str}\t{amount}\n")
        print("예산이 추가가 완료되었습니다.")
        return True
    except Exception as e:
        print(f"!오류: {setting_file_path} 파일을 쓰는 중 오류가 발생했습니다: {e}")
        return False

def modify_budget_file(date_str, amount):
    """
    설정 파일의 예산 수정
    """
    setting_file_name =user_id_global + SETTING_FILE_SUFFIX
    setting_file_path = HOME_DIR / setting_file_name
    
    lines = []
    found = False
    
    try:
        with open(setting_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        with open(setting_file_path, 'w', encoding='utf-8') as f:
            for line in lines:

                parts = line.split('\t')
                if parts[0] == date_str:
                    f.write(f"{date_str}\t{amount}\n")
                    found = True
                else:
                    f.write(line)
        
        if found:
            print(f"{date_str} 예산이 수정되었습니다.")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"!오류: {setting_file_path} 파일을 읽는 중 오류가 발생했습니다: {e}")
        return False

def delete_budget_file(date_str):
    """
    설정 파일에서 예산 삭제
    """
    setting_file_name =user_id_global + SETTING_FILE_SUFFIX
    setting_file_path = HOME_DIR / setting_file_name
    
    lines = []
    deleted = False

    print("삭제하는 중...")
    print(SEPERATOR)
    try:
        with open(setting_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        with open(setting_file_path, 'w', encoding='utf-8') as f:
            for line in lines:

                parts = line.split('\t')
                if parts[0] == date_str:
                    deleted = True
                    continue # 해당 줄 건너뛰기 (삭제)
                f.write(line)

        
        if deleted:
            print("삭제가 완료 되었습니다.")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"파일 삭제 중 오류 발생: {e}")
        return False

def budget_menu():
    """
    예산 기능 메인 메뉴
    """
    while True:
        print("[추가] [수정] [삭제] [조회]\n")
        command = input("메뉴 입력: ")
        print(SEPERATOR)

        if command == "추가":
            while 1:
                date_str = input("예산을 설정할 월을 입력하세요 (YYYY-MM) : ")
                amount_str = input("예산 금액을 입력하세요: ")
                print(SEPERATOR)
                if valid_budget_date(date_str) and valid_budget_amount(amount_str): break

            # 예산 날짜 존재여부 확인
            if not check_file_date(date_str):
                expense = calculate_budget(date_str)
                if expense is False: break
                elif int(amount_str) - expense < 0:
                    print("예산은 총 지출액보다 큰 금액으로만 설정할 수 있습니다.")
                    print(f"당월의 총 지출액: ₩{expense}")
                    print(SEPERATOR)
                    continue
                # 마지막 저장 여부
                yn = input("이대로 저장하시겠습니까? (Y/N): ").lower()
                if yn == 'y' :
                    append_budget_file(date_str, amount_str)
                    break
                elif(yn=='n'):
                    print("입력을 취소합니다.")
                    print("주 프롬프트로 돌아갑니다.")
                    print(SEPERATOR2)
                    break
            else:
                print("이미 해당 월의 예산이 존재합니다. [수정]을 이용해주세요.")
            
        elif command == "수정":
            if not calculate_budget() : break# 현재 내역 출력
            while 1:
                date_str = input("수정할 월을 입력하세요 (YYYY-MM) : ")
                amount_str = input("수정할 예산 금액을 입력하세요: ")
                if valid_budget_date(date_str) and valid_budget_amount(amount_str) :
                    if check_file_date(date_str): break
                    else: print("해당 월의 예산이 존재하지 않습니다. 다시 입력해주세요")
            
            expense = calculate_budget(date_str)
            if expense is False: break
            elif int(amount_str) - expense < 0:
                print("예산은 총 지출액보다 큰 금액으로만 설정할 수 있습니다.")
                print(f"당월의 총 지출액: ₩{expense}")
                print(SEPERATOR)
                continue
            # 마지막 저장 여부
            yn = input("이대로 저장하시겠습니까? (Y/N): ").lower()
            if yn == 'y' :
                modify_budget_file(date_str, amount_str)
            elif(yn=='n'):
                print("입력을 취소합니다.")
                print("주 프롬프트로 돌아갑니다.")
                print(SEPERATOR2)

        elif command == "삭제":
            if not calculate_budget() : break # 현재 내역 출력
            while 1:
                date_str = input("삭제할 날짜(YYYY-MM)를 입력하세요: ")
                if valid_budget_date(date_str): 
                    if check_file_date(date_str): break
                    else: print("해당 월의 예산이 존재하지 않습니다. 다시 입력해주세요")

            
            # 마지막 저장 여부
            yn = input("정말 삭제하시겠습니까? (Y/N): ").lower()
            if yn == 'y' :
                delete_budget_file(date_str)
            elif(yn=='n'):
                print("입력을 취소합니다.")
                print("주 프롬프트로 돌아갑니다.")

        elif command == "조회":
            calculate_budget()
            break
        else:
            print("입력이 올바르지 않습니다.")
    print(SEPERATOR2)
        

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
        category.load_user_categories(user_id)
        currentmap=category.get_category_map()
        category.handle_category(currentmap,user_id)
    elif(c == '예산'):
        budget_menu()
    elif(c == '로그아웃'):
        return -1
        #로그아웃 함수(메인메뉴로 돌아감)
    

def mainPrompt(user_id):
    global user_id_global 
    user_id_global = user_id
    while(1):
        c = print_mainPrompt()
        check = callFunc(c, user_id)
        if check == -1: 
            return -1     


if __name__ == "__main__":
    mainPrompt("matthew")