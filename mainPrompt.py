from fileCheck import verify_files
from query_edit import handle_query_and_display
from query_edit import handle_edit
from expense_income import expenditure
from expense_income import income
#주 프롬프트 :
SEPERATOR = '--------------------------------------------------------------'
SEPERATOR2 = '=============================================================='


def print_mainPrompt():
    print('=주 프롬프트=\n')
    print('[지출] [수입] [조회]\n[편집] [저장] [로그아웃]\n')
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
    elif(c == '저장'):
        print("저장하는 중...")
        print(SEPERATOR)
        if(verify_files()):
            print("성공적으로 저장되었습니다.\n주프롬프트로 돌아갑니다.")
            print(SEPERATOR2)
        else :  return -1
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