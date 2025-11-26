import sys
import os
import datetime
import re
from pathlib import Path

# 홈 경로 설정
HOME_DIR = Path.cwd()
# 가계부 파일 접미사
LEDGER_FILE_SUFFIX = "_HL.txt"
SEPERATOR2 = '=============================================================='

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
        elif(amount.startswith('0')):
            print("금액은 선행 0이 아닌 정수로 입력해야 합니다.")            
        elif(int(amount)<=0):
            print("금액은 양의 정수로 입력해야 합니다.")
        elif(int(amount)>10000000):
           print("금액은 10000000원 이하여야 합니다")
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

                    f.write(date+'\t'+type+'\t'+amount+'\t'+category+'\t'+method+"\n") #파일에 저장
            
                    hh = [line for line in hh if line.strip()] #빈 줄 무시

                    sum=0
                    for line in hh:
                        line=line.split()
                        if(line[1]=='E'):
                            sum=sum-int(line[2])
                        elif(line[1]=='I'):
                            sum=sum+int(line[2])
            except Exception as e:
                # 파일을 읽는 도중 인코딩 등 다른 문제가 발생했을 경우
                print(f"!치명적오류: {user_id}{LEDGER_FILE_SUFFIX} 파일을 읽는 중 오류가 발생했습니다: {e}")
                print("프로그램을 종료시킵니다.")
                sys.exit()

            if(type=='E'):
                sum=sum-int(amount)
            elif(type=='I'):
                sum=sum+int(amount)

            print("\n저장이 완료되었습니다.")
            print("현재 ID님의 총 자산은 ₩"+str(sum)+"입니다.")
            print("------------------------------------------------------------")
            break
        elif(yn=='n'):
            print("입력을 취소합니다.")
            print("주 프롬프트로 돌아갑니다.")
            print(SEPERATOR2)
            return


def expenditure(user_id):
    type='E'
    print("\n")
    date=dinput()
    category=cinput()
    amount=ainput()
    method=minput()
    print("날짜         지출    수입    카테고리    결제수단")
    print(date+"   "+amount+"    -      "+category+"        "+method)
    hsave(user_id, date, type, amount, category, method)
    
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
    


