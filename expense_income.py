import sys
import os
import datetime
import re
from pathlib import Path

# 홈 경로 설정
HOME_DIR = Path.cwd()
# 가계부 파일 접미사
LEDGER_FILE_SUFFIX = "_HL.txt"
SETTING_FILE_SUFFIX = "_setting.txt"
SEPERATOR1 = '--------------------------------------------------------------'
SEPERATOR2 = '=============================================================='

user_id_global = ''
cat1={'식비','음식','밥','food','식'}
cat2={'교통','차','지하철','transport','transportation','교'}
cat3={'주거','월세','관리비','housing','house','rent','주'}
cat4={'여가','취미','문화생활','hobby','leisure','여'}
cat5={'입금','월급','용돈','sallary','wage','income','입'}
cat6={'기타','etc','other','기'}

meth1={'현금','cash','지폐','현'}
meth2={'카드','card','credit','카'}
meth3={'계좌이체','transfer','bank','account','송금','계'}

def valid_date(date_str):
    """날짜 유효성 검사 및 반환 (5.2.1.1 ~ 5.2.1.4절)"""
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_str):
        print("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")
        return 0
    try:
        y, m, d = map(int, date_str.split('-'))
        date_obj = datetime.date(y, m, d)
    except ValueError:
        print("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")
        return 0
    if(y>2099 or y<1900):
        print("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")
        return 0
    elif(date_obj > datetime.date.today()):
        print("오늘 이후의 날짜는 입력할 수 없습니다.")
        return 0
    return 1

def dinput():
    #date=input('날짜 입력(YYYY-MM-DD): ')
    #print("------------------------------------------------------------")
    #tokens=date.split('-')
    #print(tokens)
    while 1:
        date=input('날짜 입력(YYYY-MM-DD): ')
        print("------------------------------------------------------------")
        if(valid_date(date)==1):
            break
    return date

def cinput():
    print("카테고리")
    print(" [식비][교통][주거][여가][기타]\n")
    while 1:
        category=input('카테고리 입력: ')
        if(category in cat1):
            category='식비'
            break
        elif(category in cat2):
            category='교통'
            break
        elif(category in cat3):
            category='주거'
            break
        elif(category in cat4):
            category='주거'
            break
        elif(category in cat6):
            category='기타'
            break
        else:
            print("올바른 카테고리를 입력해야 합니다.")
    print("------------------------------------------------------------")
    return category

def ainput():
    while 1:
        amount=input('금액 입력: ')
        if(not amount.isdecimal()):#문자열이 수로 이루어져 있는지 검사
            print("금액은 정수로 입력해야 합니다.")     
        elif(int(amount)<=0):
            print("금액은 양의 정수로 입력해야 합니다.")
        elif(amount.startswith('0')):
            print("금액은 정수로 입력해야 합니다.")       
        elif(int(amount)>999999999):
           print("금액은 999,999,999 이하의 값만 허용됩니다.")
        else:
            break
    print("------------------------------------------------------------")
    return amount

def minput():
    print("결제수단")
    print(" [카드][현금][계좌이체]\n")
    while 1:
        method=input('결제수단 입력: ')
        if(method in meth1):
            method='현금'
            break
        elif(method in meth2):
            method='카드'
            break
        elif(method in meth3):
            method='계좌이체'
            break
        else:
            print("올바른 결제수단을 입력해야 합니다.")
    print("------------------------------------------------------------")
    return method

def hsave(user_id, date, type, amount, category, method):
    while 1:
        yn=input("\n이대로 저장하시겠습니까?(Y/N): ")#Y/N 대소문자 구분?
        yn=yn.lower()
        print("")
        
        if(yn=='y'):
            ledger_file_name = f"{user_id}{LEDGER_FILE_SUFFIX}"
            ledger_file_path = HOME_DIR / ledger_file_name
            try:
                with open(ledger_file_path, 'a+', encoding='utf-8') as f:
                    f.seek(0)
                    hh=f.readlines() #파일 불러오기
                    f.seek(0,2)
                    for line in hh: #줄바꿈문자 유무 확인 후 추가
                        if not line.endswith('\n'):
                            f.write("\n")

                    #지출이 수입보다 큰경우 계산
                    hh = [line for line in hh if line.strip()] #빈 줄 무시
                    sum=0
                    for line in hh:
                        line=line.split()
                        if(line[1]=='E'):
                            sum=sum-int(line[2])
                        elif(line[1]=='I'):
                            sum=sum+int(line[2])
                    origin_sum = sum
                    if type == 'I' :
                        sum += int(amount)
                    else :
                        sum -= int(amount)
                    if sum < 0 :
                        print(SEPERATOR1)
                        print("현재 지출이 수입보다 커집니다.")
                        print(f"현재 {user_id}님의 총 자산은 ₩{origin_sum}입니다.")
                        print(SEPERATOR1)
                        return False            

                    f.write(date+'\t'+type+'\t'+amount+'\t'+category+'\t'+method+"\n") #파일에 저장
            
            except Exception as e:
                # 파일을 읽는 도중 인코딩 등 다른 문제가 발생했을 경우
                print(f"!치명적오류: {user_id}{LEDGER_FILE_SUFFIX} 파일을 읽는 중 오류가 발생했습니다: {e}")
                print("프로그램을 종료시킵니다.")
                sys.exit()

            print("\n저장이 완료되었습니다.")
            print("현재 ID님의 총 자산은 ₩"+str(sum)+"입니다.")
            print("------------------------------------------------------------")
            return True
        elif(yn=='n'):
            print("입력을 취소합니다.")
            print("주 프롬프트로 돌아갑니다.")
            print(SEPERATOR2)
            return True
        
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
                    elif(b_date == date_str):
                        budgets[date_str] = b_amount
    
                
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
    is_expenses_exist = date_str in expenses
    if date_str and is_expenses_exist:
        diff = budgets[date_str]-expenses[date_str]
        if diff >= 0 :
            print(f"{date_str:<8} 예산 금액:{budgets[date_str]:>10} / 예산 금액:{diff:>10}")
        else :
            print("예산을 초과하였습니다!")
            print(f"{date_str} 예산 금액:{budgets[date_str]:>10} / 예산 초과 금액:{diff:>10}")
        return True
    elif date_str and not is_expenses_exist :
        return False
    
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

def expenditure(user_id):
    type='E'
    global user_id_global
    user_id_global = user_id
    print("\n")
    date=dinput()
    category=cinput()
    amount=ainput()
    method=minput()
    print("날짜         지출    수입    카테고리    결제수단")
    print(date+"   "+amount+"    -      "+category+"        "+method)
    while not hsave(user_id, date, type, amount, category, method) :
        amount = ainput()
        print("날짜         지출    수입    카테고리    결제수단")
        print(date+"   "+amount+"    -      "+category+"        "+method)
    calculate_budget(date[0:7])

def income(user_id):
    type='I'
    print("\n")
    date=dinput()
    category='입금'
    amount=ainput()
    method=minput()
    print("날짜         지출    수입    카테고리    결제수단")
    print(date+"     -     "+amount+"     "+category+"        "+method)
    hsave(user_id, date, type, amount, category, method)
    

