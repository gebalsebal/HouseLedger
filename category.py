import os
from pathlib import Path

import re
from query_edit import load_user_ledger, save_ledger_data

HOME_DIR = Path.cwd()
SETTING_FILE_SUFFIX = "_setting.txt"

# 로그인 시 로드될 전역 카테고리 맵
# 키: 표준명 (str), 값: {'separator': str, 'synonyms': list of str}
USER_CATEGORY_MAP = {} 

# 회원가입 시 사용할 기본 카테고리 맵
DEFAULT_CATEGORIES = {
    '입금': {'separator': 'C1', 'synonyms': ['월급', '용돈', 'salary', 'wage', 'income', '입']},
    '식비': {'separator': 'C2', 'synonyms': ['음식', '밥', 'food', '식']},
    '교통': {'separator': 'C3', 'synonyms': ['차', '지하철', 'transport', 'transportation', '교']},
    '주거': {'separator': 'C4', 'synonyms': ['월세', '관리비', 'housing', 'house', 'rent', '주']},
    '여가': {'separator': 'C5', 'synonyms': ['취미', '문화생활', 'hobby', 'leisure', '여']},
    '기타': {'separator': 'C6', 'synonyms': ['etc', 'other', '기']},
}

PAYMENT_MAP = {
    '현금': {'synonyms': ['cash', '지폐', '현']},
    '카드': {'synonyms': ['card', 'credit', '카']},
    '계좌이체': {'synonyms': ['transfer', 'bank', 'account', '송금', '계']},
}

# 카테고리 맵 관리 및 파일 I/O 함수

def create_default_settings(user_id):
    """
    회원가입 시 호출되어 <ID>_setting.txt 파일을 생성하고 기본 카테고리 저장.
    """
    settings_file_path = HOME_DIR / f"{user_id}{SETTING_FILE_SUFFIX}"
    category_lines = []
    
    # 카테고리 섹션 내용 생성 (형식: 구분자\t표준명\t동의어)
    for standard_name, data in DEFAULT_CATEGORIES.items():
        separator = data['separator']
        # 동의어는 탭 문자로 구분되어 파일에 저장됩니다.
        synonyms_str = '\t'.join(data['synonyms'])
        
        # 형식: <Category구분자><탭><Category표준명><탭><Category동의어>
        line = f"{separator}\t{standard_name}\t{synonyms_str}"
        category_lines.append(line)

    # 카테고리 섹션과 예산 섹션을 빈 줄로 구분 
    content = '\n'.join(category_lines) + '\n\n' 
    
    try:
        with open(settings_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"오류: 설정 파일 생성 중 문제 발생: {e}")
        return False


def load_user_categories(user_id):
    """
    로그인 시 호출되어 <ID>_setting.txt 파일에서 카테고리 정보 로드.
    """
    global USER_CATEGORY_MAP
    settings_file_path = HOME_DIR / f"{user_id}{SETTING_FILE_SUFFIX}"
    
    if not settings_file_path.exists():
        return False 

    USER_CATEGORY_MAP = {}
    
    try:
        with open(settings_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    break # 빈 줄(카테고리 섹션 끝) 발견
                
                parts = line.split('\t')
                
                if len(parts) < 2:
                    return False 
                
                separator = parts[0].strip()
                standard_name = parts[1].strip()
                synonyms = [p.strip() for p in parts[2:] if p.strip()]

                USER_CATEGORY_MAP[standard_name] = {
                    'separator': separator,
                    'synonyms': synonyms
                }
                
        return True
        
    except Exception as e:
        print(f"오류: 설정 파일 로드 중 문제 발생: {e}")
        return False


def get_category_map():
    """
    현재 메모리에 로드된 USER_CATEGORY_MAP의 참조 반환.
    """
    global USER_CATEGORY_MAP
    return USER_CATEGORY_MAP

def get_payment_map():
    """
    현재 메모리에 로드된 PAYMENT_MAP의 참조 반환.
    """
    global PAYMENT_MAP
    return PAYMENT_MAP


def save_user_settings(user_id, map_data):
    """
    변경된 카테고리 맵을 파일에 저장. (예산 데이터와 함께 저장해야 함)
    """
    settings_file_path = HOME_DIR / f"{user_id}{SETTING_FILE_SUFFIX}"

    budget_lines = []
    try:
        if settings_file_path.exists():
            with open(settings_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # 카테고리 섹션과 예산 섹션을 구분하는 빈 줄('\n')을 찾아 그 이후를 예산으로 추출
            found_separator = False
            for line in lines:
                if found_separator:
                    # 빈 줄 이후의 모든 줄은 예산 데이터.
                    budget_lines.append(line.rstrip('\n'))
                elif line.strip() == '':
                    # 첫 번째 빈 줄 발견 시, 다음 줄부터 예산 섹션으로 간주.
                    found_separator = True
                    
    except Exception as e:
        print(f"!치명적오류: 기존 설정 파일({settings_file_path}) 읽기 중 오류 발생: {e}")
        return False
        
    category_lines = []
    # 1. 카테고리 섹션 내용 생성
    for standard_name, data in map_data.items():
        separator = data['separator']
        synonyms_str = '\t'.join([s for s in data.get('synonyms', []) if s.strip()])
        # 형식: <Category구분자>\t<Category표준명>[\t<Category동의어>]
        line = f"{separator}\t{standard_name}"
        if synonyms_str:
            line += f"\t{synonyms_str}"
        category_lines.append(line)

    # 2. 카테고리 섹션과 예산 섹션을 빈 줄로 구분
    content = '\n'.join(category_lines) + '\n\n'
    # 3. 기존 예산 섹션 추가
    content += '\n'.join([line for line in budget_lines if line.strip()])

    try:
        with open(settings_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"오류: 설정 파일 저장 중 문제 발생: {e}")
        return False
    








def search_category(category_map, searchcat):
    std_category=None
    for key, value in category_map.items():
        if(searchcat == key):
            std_category=key
        elif(searchcat in value["synonyms"]):
            std_category=key
    return std_category


def add_category(category_map,user_id):
    #표준명 입력 및 오류처리
    while 1:
        stdcat=input("\n표준명 입력: ")
        if(any(not (('가' <= char <= '힣') or char.isalnum()) for char in stdcat)):
            print("한글, 알파벳 대문자 A~Z, 소문자 a~z, 정수 0~9 이외의 문자는 허용하지 않습니다.")
        elif(search_category(category_map,stdcat)!=None):
            print("이미 존재하는 표준명 또는 동의어입니다.")
        else:
            break
    #카테고리 구분자 할당 (규칙?) -> 전체 카테고리 구분자 중 제일 큰 값보다 1 크게 설정 
    sep=[details['separator'] for details in category_map.values()]
    nsep=max(int(separator[1:]) for separator in sep)+1
    #맵에 카테고리 표준명 추가
    category_map[stdcat]={'separator':"C"+str(nsep),'synonyms':[]}
    #동의어 입력 및 오류처리
    while 1:
        addlist=input("동의어 입력(공백으로 구분, 동의어를 설정하지 않으려면 enter입력): ")
        print("\n-------------------------")
        addlist=addlist.split()
        dup=0
        #동의어들 끼리 겹치는 경우 고려
        if(len(addlist) != len(set(addlist))):
            dup=3
        for i in addlist:
            if(any(not (('가' <= char <= '힣') or char.isalnum()) for char in i)):
                dup=2
                break
            elif(search_category(category_map,i)!=None):
                dup=1
        if(dup==1):
            print("이미 존재하는 표준명 또는 동의어입니다.")
        elif(dup==2):
            print("한글, 알파벳 대문자 A~Z, 소문자 a~z, 정수 0~9 이외의 문자는 허용하지 않습니다.")
        elif(dup==3):
            print("중복되는 동의어들을 입력할 수 없습니다.")
        elif(dup==0):
            break
    #맵에 카테고리 동의어 추가
    category_map[stdcat]["synonyms"]=addlist
    #저장여부 확인
    while 1:
        yn=input("이대로 저장하시겠습니까?(Y/N): ")
        yn=yn.lower()
        if(yn=='y'):
            #사용자 설정 파일에 저장
            save_user_settings(user_id, category_map)
            print("\n'"+stdcat+"' 카테고리가 성공적으로 추가되었습니다.")
            print("-------------------------")
            break
        elif(yn=='n'):
            #맵에서 카테고리 삭제하여 저장취소
            del category_map[stdcat]
            print("\n저장을 취소합니다.")
            break
         
def update_category(category_map,user_id):
    print("   카테고리")
    print("\t",end="")
    #카테고리 표준명 종류 출력
    for key in category_map:
        print(key,end='\t')
    #수정할 카테고리 표준명 입력 및 오류처리
    while 1:
        ostdcat=input("\n 수정할 카테고리 선택: ")
        if(search_category(category_map,ostdcat)==None):
            print("존재하지 않는 카테고리 표준명입니다.")
        elif(search_category(category_map,ostdcat)!=ostdcat):
            print("수정할 카테고리의 표준명을 입력해야 합니다.")
        else:
            break
    #현재 동의어 출력
    print("현재 동의어:",end=" ")
    outstr=', '.join(category_map[ostdcat]["synonyms"])
    print(outstr)
    print("=========================")
    #카테고리 수정명 입력 및 오류처리
    while 1:
        nstdcat=input("\n 카테고리 수정명 입력: ")
        if(any(not (('가' <= char <= '힣') or char.isalnum()) for char in nstdcat)):
            print("한글, 알파벳 대문자 A~Z, 소문자 a~z, 정수 0~9 이외의 문자는 허용하지 않습니다.")
        elif(search_category(category_map,nstdcat)!=None):
            print("이미 존재하는 표준명 또는 동의어입니다.")
        else:
            break
    #맵에 수정명으로 수정(새로운 항목 추가 및 기존 항목 삭제)
    category_map[nstdcat]=category_map[ostdcat]
    osynonyms=category_map[ostdcat]["synonyms"]#수정전 카테고리 동의어
    category_map[nstdcat]["synonyms"]=[]#수정후 카테고리 동의어는 일단 빈집합
    del category_map[ostdcat]
    #동의어 입력 및 오류처리
    while 1:
        corlist=input("동의어 입력(공백으로 구분, 기존의 동의어를 삭제하려면 '-' 입력): ")
        if(corlist=='-'):
            corlist=[]
            break
        elif(corlist==''):
            corlist=osynonyms
            break
        else:
            corlist=corlist.split()
            dup=0
            if(len(corlist) != len(set(corlist))):
                dup=3
            for i in corlist:
                if(any(not (('가' <= char <= '힣') or char.isalnum()) for char in i)):
                    dup=2
                    break
                elif(search_category(category_map,i)!=None):
                    dup=1
            if(dup==1):
                print("이미 존재하는 표준명 또는 동의어입니다.")
            elif(dup==2):
                print("한글, 알파벳 대문자 A~Z, 소문자 a~z, 정수 0~9 이외의 문자는 허용하지 않습니다.")
            elif(dup==3):
                print("중복되는 동의어들을 입력할 수 없습니다.")
            elif(dup==0):
                break
    #맵에 카테고리 동의어 추가
    category_map[nstdcat]["synonyms"]=corlist
    #저장여부 확인
    while 1:
        print("-------------------------")
        yn=input("이대로 저장하시겠습니까?(Y/N): ")
        print(osynonyms)
        yn=yn.lower()
        if(yn=='y'):
            #사용자 설정 파일에 저장
            save_user_settings(user_id,category_map)
            print("\n'"+nstdcat+"' 카테고리가 성공적으로 수정되었습니다.")
            print("-------------------------")  
        elif(yn=='n'):
            #맵에서 카테고리 원상복구
            category_map[ostdcat]=category_map[nstdcat]
            category_map[ostdcat]["synonyms"]=osynonyms
            del category_map[nstdcat]
            print("\n저장을 취소합니다.")
        break

def delete_category(category_map,user_id):
    #입금카테고리 표준명
    for key,value in category_map.items():
        if value['separator']=='C1':
            income=key
    print("   카테고리")
    print("\t",end="")
    #카테고리 표준명 종류 출력
    for key in category_map:
        print(key,end='\t')
    #카테고리 표준명 입력 및 오류처리
    while 1:
        stdcat=input("\n 삭제할 카테고리 선택: ")
        if(search_category(category_map,stdcat)==None):
            print("존재하지 않는 카테고리 표준명입니다.")
        elif(search_category(category_map,stdcat)!=stdcat):
            print("삭제할 카테고리의 표준명을 입력해야 합니다.")
        elif(search_category(category_map,stdcat)==income):
            print("입금 카테고리는 삭제할 수 없습니다.")
        else:
            break
    #삭제여부 확인
    while 1:
        print("-------------------------")
        yn=input("정말 삭제하시겠습니까?(Y/N): ")
        yn=yn.lower()
        if(yn=='y'):
            print("\n삭제하는 중...")
            print("-------------------------")
            #print(category_map[stdcat]["separator"])
            #가계부 파일에서 삭제할 카테고리로 저장된 항목 카테고리 변경
            data=load_user_ledger(user_id)

            target_separator = category_map[stdcat]["separator"]
            separator_char = " " 

            for item in data:
                category_string = item['카테고리']
                if not category_string:
                    continue
                current_separators = re.split(separator_char, category_string)
                updated_separators = [
                    sep for sep in current_separators 
                    if sep and sep != target_separator
                ]
                item['카테고리'] = separator_char.join(updated_separators)
            save_ledger_data(user_id,data)


            #for item in data:
                #print(item['카테고리'])
            #    if(item['카테고리']==category_map[stdcat]["separator"]):
            #        item['카테고리']=""
            #save_ledger_data(user_id,data)
            
            #맵에서 카테고리 삭제
            del category_map[stdcat]
            #사용자 설정파일에서 삭제
            save_user_settings(user_id,category_map)
            print("\n삭제가 완료되었습니다.")
            print("-------------------------")  
        elif(yn=='n'):
            print("\n삭제를 취소합니다.")
        break 
    
def handle_category(category_map,user_id):
    print("[추가] [수정] [삭제]")
    choice=input("메뉴 입력: ")
    print("-------------------------")
    if(choice=="추가"):
        add_category(category_map,user_id)
    elif(choice=="수정"):
        update_category(category_map,user_id)
    elif(choice=="삭제"):
        if(len(category_map)>=3):
            delete_category(category_map,user_id)
        else:
            print("카테고리는 입금 카테고리를 포함하여 최소 2개 이상 있어야 합니다.")

