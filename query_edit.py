import sys
import os
import datetime
import re
from pathlib import Path

# --------------------------------------------------------------
# 1. 전역 상수/변수 및 헬퍼 함수 (Validation Logic)
# --------------------------------------------------------------

# 💡 카테고리/결제수단 표준명 및 동의어 정의
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


def get_valid_date(date_str, is_edit_mode=False):
    """날짜 유효성 검사 및 반환 (5.2.1.1 ~ 5.2.1.4절)"""
    
    if not date_str or date_str.isspace() or date_str.strip() != date_str:
        raise ValueError("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")

    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_str):
        raise ValueError("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")

    try:
        y, m, d = map(int, date_str.split('-'))
        date_obj = datetime.date(y, m, d)
    except ValueError:
        raise ValueError("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")

    if not (1900 <= y <= 2099):
        raise ValueError("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")

    if is_edit_mode and date_obj > datetime.date.today():
        raise ValueError("오늘 이후의 날짜는 입력할 수 없습니다.")
    
    return date_str

def get_valid_date_or_month(date_input):
    """5.3.1절: YYYY-MM-DD 또는 YYYY-MM 형식 검사"""
    
    date_input = date_input.strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_input):
        return date_input
    elif re.fullmatch(r'\d{4}-\d{2}', date_input):
        return date_input
    else:
        raise ValueError("날짜는 YYYY-MM-DD 또는 YYYY-MM 형식이어야 합니다.")


def get_valid_amount(amount_str):
    """금액 유효성 검사 및 정수 반환 (5.2.3.1 ~ 5.2.3.4절)"""
    
    if not amount_str or amount_str.isspace() or amount_str.strip() != amount_str:
        raise ValueError("금액은 정수로 입력해야 합니다.")
    
    amount_str = amount_str.strip()
    
    try:
        amount = int(amount_str)
    except ValueError:
        raise ValueError("금액은 정수로 입력해야 합니다.")
    
    if amount <= 0:
        raise ValueError("금액은 양의 정수로 입력해야 합니다.")
    
    if amount_str != str(amount) :
        raise ValueError("금액은 정수로 입력해야 합니다.")
        
    if amount > 999999999 or len(amount_str) > 9: 
        raise ValueError("금액은 999,999,999 이하의 값만 허용됩니다.")
        
    return amount


def get_valid_category(category_input):
    """카테고리 유효성 검사 및 표준명 반환 (5.2.4.1 ~ 5.2.4.4절)"""
    
    if not category_input or category_input.isspace():
        raise ValueError("올바른 카테고리를 입력해야 합니다.")

    if category_input.strip() != category_input:
        raise ValueError("올바른 카테고리를 입력해야 합니다.")
        
    if ' ' in category_input:
        raise ValueError("올바른 카테고리를 입력해야 합니다.")

    #if type_str == 'I'
    #    return '입금'
        
    input_stripped = category_input.strip()
    input_lower = input_stripped.lower()
    
    for standard_name, synonyms in CATEGORY_MAP.items():
        #if standard_name == '입금': continue
        
        if standard_name.lower() == input_lower or input_lower in [s.lower() for s in synonyms]:
            return standard_name
            
    raise ValueError("올바른 카테고리를 입력해야 합니다.")


def get_valid_payment(payment_input):
    """결제수단 유효성 검사 및 표준명 반환 (5.2.5.1 ~ 5.2.5.4절)"""
    
    if not payment_input or payment_input.isspace():
        raise ValueError("올바른 결제수단을 입력해야 합니다.")

    if payment_input.strip() != payment_input:
        raise ValueError("올바른 결제수단을 입력해야 합니다.")
        
    if ' ' in payment_input:
        raise ValueError("올바른 결제수단을 입력해야 합니다.")
    
    input_stripped = payment_input.strip()
    input_lower = input_stripped.lower()
    
    for standard_name, synonyms in PAYMENT_MAP.items():
        if standard_name.lower() == input_lower or input_lower in [s.lower() for s in synonyms]:
            return standard_name
            
    raise ValueError("올바른 결제수단을 입력해야 합니다.")

# --------------------------------------------------------------
# 2. 데이터 관리 함수 (I/O & Utilities)
# --------------------------------------------------------------


def load_user_ledger(user_id):
    """
    사용자의 가계부 파일(<ID>_HL.txt)을 읽어 리스트로 반환 (6.2절)
    실제 파일 I/O 및 6.3절 문법 검사 로직이 필요함.
    """
    file_path = f"{user_id}_HL.txt"
    data = []
    
    try:
        # 파일이 없으면 빈 리스트 반환 (6.3.1.b절: 재시작 대신 빈 리스트)
        if not os.path.exists(file_path):
            print(f"!오류: 가계부 파일이 존재하지 않습니다. 새로운 파일 생성.")
            with open(file_path, 'w', encoding='utf-8') as f:
                pass
            return data

        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line: continue
                
                # 6.2.1절 문법 검사: <Date><탭문자><Type><탭문자><Amount>...
                parts = line.split('\t')
                if len(parts) != 5:
                    print(f"!치명적오류: 현재 {file_path} {i}행에서 오류가 발생되었습니다.")
                    print("프로그램을 종료시킵니다.")
                    sys.exit()
                
                # 날짜, 유형, 금액, 카테고리, 결제수단
                data.append({
                    'idx': i, # 임시 인덱스 (삭제/수정 시 중요)
                    '날짜': parts[0],
                    '유형': parts[1],
                    '금액': int(parts[2]),
                    '카테고리': parts[3],
                    '결제수단': parts[4],
                })
        
        # 7.8절에 따라 날짜 역순으로 정렬 (가정)
        return sorted(data, key=lambda x: x['날짜'], reverse=True)
        
    except Exception as e:
        print(f"!치명적오류: {file_path} 파일을 읽는 중 오류가 발생했습니다: {e}")
        print("프로그램을 종료시킵니다.")
        sys.exit()


def calculate_total_asset(data_list):
    """가계부 내역 리스트를 기반으로 총 자산을 계산 (7.8, 7.9절)"""
    total = 0
    for item in data_list:
        amount = item['금액']
        if item['유형'] == 'I':
            total += amount
        elif item['유형'] == 'E':
            total -= amount
    return total


def save_ledger_data(user_id, data_list):
    """
    변경된 가계부 내역을 파일에 저장하고 무결성 검사 (7.10, 6.3절)
    """
    file_path = f"{user_id}_HL.txt"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data_list:
                # 6.2.1절 형식: <Date><탭문자><Type><탭문자><Amount><탭문자><Category><탭문자><Payment>
                line = f"{item['날짜']}\t{item['유형']}\t{item['금액']}\t{item['카테고리']}\t{item['결제수단']}\n"
                f.write(line)
        
        # (6.3절 파일 검사는 load_user_ledger를 호출하여 수행 가능하나, 중복을 막기 위해 생략)
        # 이 시점에서 저장된 파일이 문법적으로 올바른지 다시 load_user_ledger를 통해 확인해야 함.
        return True
        
    except Exception as e:
        print(f"!치명적오류: {file_path} 파일을 저장하는 중 오류가 발생했습니다: {e}")
        print("프로그램을 종료시킵니다.")
        sys.exit()

# --------------------------------------------------------------
# 3. 조회 및 편집 기능 (Ledger Features)
# --------------------------------------------------------------

# 💡 조회 필터링 헬퍼 함수 (표준명 찾기)
def _get_standard_name(input_str, item_map):
    """주어진 맵에서 입력 문자열에 해당하는 표준명을 찾습니다. 없으면 None 반환."""
    input_lower = input_str.strip().lower()
    
    for standard_name, synonyms in item_map.items():
        if standard_name.lower() == input_lower or input_lower in [s.lower() for s in synonyms]:
            return standard_name
            
    return None

def _filter_ledger_data(data_list, search_term):
    """검색 조건(날짜/카테고리/결제수단)에 따라 데이터를 필터링"""
    filtered_data = []
    
    # 1. 날짜/연월 검색 판단
    if search_term and search_term[0].isdigit():
        try:
            get_valid_date_or_month(search_term) # 형식만 검사 (5.3.1절)
            for item in data_list:
                if item['날짜'].startswith(search_term):
                    filtered_data.append(item)
            return filtered_data
        except ValueError as e:
                print(f"오류 메시지: {e}")
                return -2

    # 2. 카테고리 검색 판단 (표준명 또는 동의어 사용)
    standard_category = _get_standard_name(search_term, CATEGORY_MAP)
    if standard_category:
        for item in data_list: 
            if item['카테고리'] == standard_category:
                filtered_data.append(item)
        return filtered_data
    
    # 3. 결제수단 검색 판단 (표준명 또는 동의어 사용)
    standard_payment = _get_standard_name(search_term, PAYMENT_MAP)
    if standard_payment:
        for item in data_list:
            if item['결제수단'] == standard_payment:
                filtered_data.append(item)
        return filtered_data

    return -1

def _display_ledger_table(data_list, user_id, mode="query", total_asset_data_list=None):
    """조회 결과를 UI/UX에 맞게 표 형태로 출력 (7.8절)"""
    if mode=="query":
        print("번호|     날짜      | 지출    | 수입     | 카테고리| 결제수단")
        print("--------------------------------------------------------------")
    
    asset_list_to_use = total_asset_data_list if total_asset_data_list is not None else data_list
   
    display_to_original_idx_map = []
    #idxList = []
    cnt = 1
    
    for item in data_list:
        expense = f"{item['금액']:,}" if item['유형'] == 'E' else '-'
        income = f"{item['금액']:,}" if item['유형'] == 'I' else '-'
        #idxList.append(item['idx'])
        display_to_original_idx_map.append(item['idx'])
        if mode=="query":
            print(f" {cnt:<3}| {item['날짜']:<13} |{expense:>8} | {income:>8} | {item['카테고리']:<6}| {item['결제수단']:<6}")
        cnt += 1
    
    if mode=="query":
        print("--------------------------------------------------------------")
    
    total_asset = calculate_total_asset(asset_list_to_use)
    if mode=="query":
        print(f"현재 ID님의 총 자산은 ₩{total_asset:,}입니다.")
        print("-------------------------------------------------------------")
    
    return display_to_original_idx_map  

# 💡 [조회 함수] handle_query_and_display
def handle_query_and_display(user_id, mode = "query"):
    """조회 기능의 전체 흐름을 담당하고, 필터링된 리스트를 반환 (7.8절)"""
    original_data_list = load_user_ledger(user_id) 
    
    if mode == "query":

        # print("메뉴를 입력하세요: 조회")
        # print("--------------------------------------------------------------")

        pass
    while True:
        print("\n[ 전체조회 ]   [ 검색조회 ]")
        menu = input("\n메뉴 입력: ").strip()
        print("--------------------------------------------------------------")

        if menu == "전체조회":
            if original_data_list:
                _display_ledger_table(original_data_list, user_id, mode="query", total_asset_data_list=original_data_list)
                return original_data_list
            else:
                print("검색 결과가 없습니다.")
                return [] # 빈 리스트 반환하여 편집 모드에서 '조회할 내역 없음' 처리 유도
            
        elif menu == "검색조회":
            
            print("\n입력 형식")
            print("   날짜 (YYYY-MM-DD 또는 YYYY-MM)")
            print("   카테고리")
            print("           [식비] [교통] [주거] [여가] [기타] [입금]")
            print("   결제수단")
            print("           [카드] [현금] [계좌이체]")
            
            search_term = input("\n검색 조건 입력: ").strip()
            print("--------------------------------------------------------------")
            
            filtered_data = _filter_ledger_data(original_data_list, search_term)
          
            if filtered_data == -1 or filtered_data == -2:
                if filtered_data == -1:
                    print("입력이 올바르지 않습니다.")
                continue
            elif filtered_data:
                _display_ledger_table(filtered_data, user_id, mode="query", total_asset_data_list=original_data_list)
                return filtered_data
            elif not filtered_data:
                print("검색 결과가 없습니다.")
                continue
                
        else:
            print("입력이 올바르지 않습니다.")
            continue


# 💡 [편집 함수 헬퍼] _format_item_for_display
def _format_item_for_display(item):
    """UI/UX에 맞게 내역을 포맷팅하는 헬퍼 함수"""
    date = item['날짜']
    expense = f"{item['금액']:,}" if item['유형'] == 'E' else '-'
    income = f"{item['금액']:,}" if item['유형'] == 'I' else '-'
    category = item['카테고리']
    payment = item['결제수단']
    
    return f"{date:<13}   {expense:<10}  {income:<10}  {category:<8}  {payment}"


# 💡 [편집 함수] handle_edit
def handle_edit(user_id):
    """가계부 편집 기능의 전체 흐름을 담당 (7.9절)"""
    
    print("메뉴를 입력하세요: 편집")
    print("--------------------------------------------------------------")
    
    data_for_display = handle_query_and_display(user_id, mode="edit")
    
    if not data_for_display:
        print("조회할 내역이 없습니다. 주 프롬프트로 돌아갑니다.")
        return
    
    display_to_original_idx_map = _display_ledger_table(data_for_display, user_id, mode="edit")
    
    print("===================================")
    while True:
        try:
            edit_idx_input = input("편집을 원하는 칸의 번호를 입력하세요: ").strip()
            
            if not edit_idx_input.isdigit():
                print("입력이 올바르지 않습니다.")
                continue
            
            #idxLsit[linput]
            #edit_idx = int(edit_idx_input)
            display_num = int(edit_idx_input) 
            map_index = display_num - 1

            if 0 <= map_index < len(display_to_original_idx_map):
                # 매핑 리스트에서 실제 레코드의 고유 인덱스(item['idx'])를 가져옵니다.
                original_idx_to_edit = display_to_original_idx_map[map_index] 
            else:
                print("입력이 올바르지 않습니다. 표시된 번호 내에서 선택하세요.")
                continue
            
            selected_item = next((item for item in data_for_display if item['idx'] == original_idx_to_edit), None)

            if selected_item is None:
                print("입력이 올바르지 않습니다.")
                continue
            
            print("\n편집 기능")
            print("      [ 수정 ]  [ 삭제 ]")
            while True:
                edit_action = input("\n원하는 기능을 입력하세요: ").strip()
                
                if edit_action == "수정":
                    return process_update(user_id, selected_item)
                elif edit_action == "삭제":
                    return process_delete(user_id, selected_item)
                else:
                    print("입력이 올바르지 않습니다.")
                    continue

        except Exception:
            print("입력이 올바르지 않습니다.")
            
# 💡 [편집 수정 함수] process_update
def process_update(user_id, target_item):
    """선택된 내역을 수정하고 저장 처리 (7.9절)"""
    original_data_list = load_user_ledger(user_id) # 원본 데이터 로드
    
    # target_item의 참조를 원본 리스트에서 업데이트
    # (load_user_ledger가 복사본을 주므로, 실제 변경할 항목을 원본에서 찾아야 함)
    current_item = next(item for item in original_data_list if item['idx'] == target_item['idx'])

    print("===================================")
    
    # 날짜 입력 및 유효성 검사
    while True:
        new_date = input("날짜 입력(YYYY-MM-DD): ") #strip 제거하여 공백 검사

        if not new_date:
            break
        try:
            current_item['날짜'] = get_valid_date(new_date, is_edit_mode=True)
            break
        except ValueError as e:
            print(f"오류 메시지: {e}")
            

    print("--------------------------------------------------------------")
    # 카테고리 입력 및 유효성 검사
    print("카테고리")
    print("      [식비] [교통] [주거] [여가] [기타] [입금]")
    while True:
        new_category = input("카테고리 입력: ")

        if not new_category:
            break
        try:
            standard_category = get_valid_category(new_category) # 💡 [수정] type_str 인자 제거
            
            # 💡 [수정] 카테고리에 따라 유형(Type)을 자동으로 업데이트
            if standard_category == '입금':
                current_item['유형'] = 'I'
            else:
                current_item['유형'] = 'E'
            current_item['카테고리'] = standard_category
            break
        except ValueError as e:
            print(f"오류 메시지: {e}")

    print("--------------------------------------------------------------")
    # 금액 입력 및 유효성 검사
    while True:
        new_amount = input("금액 입력: ")

        if not new_amount:
            break
        try:
            current_item['금액'] = get_valid_amount(new_amount)
            break
        except ValueError as e:
            print(f"오류 메시지: {e}")

    print("--------------------------------------------------------------")
    # 결제수단 입력 및 유효성 검사
    print("결제수단")
    print("      [카드] [현금] [계좌이체]")
    while True:
        new_payment = input("결제수단 입력: ")

        if not new_payment:
            break
        try:
            current_item['결제수단'] = get_valid_payment(new_payment)
            break
        except ValueError as e:
            print(f"오류 메시지: {e}")
    
    # 7.9절: 수정된 내용 출력
    print("===================================")
    print(f"{'날짜':<11}   {'지출':<8}  {'수입':<8}  {'카테고리':<6}  {'결제수단'}")
    print(_format_item_for_display(current_item))
    print("===================================")

    # 저장 확인 및 최종 처리
    confirm = input("이대로 저장하시겠습니까?(Y/N): ").strip().upper()
    if confirm == 'Y':
        save_ledger_data(user_id, original_data_list)
        total_asset = calculate_total_asset(original_data_list)
        
        print("\n편집이 완료되었습니다.")
        print(f"현재 ID님의 총 자산은 ₩{total_asset:,}입니다.")
        print("--------------------------------------------------------------")
        return True
    else:
        print("입력을 취소합니다. 주 프롬프트로 돌아갑니다.")
        return True

# 💡 [편집 삭제 함수] process_delete
def process_delete(user_id, target_item):
    """선택된 내역을 삭제하고 저장 처리 (7.9절)"""
    original_data_list = load_user_ledger(user_id)
    
    print("===================================")
    print(f"{'날짜':<11}   {'지출':<8}  {'수입':<8}  {'카테고리':<6}  {'결제수단'}")
    print(_format_item_for_display(target_item))
    print("===================================")

    confirm = input("정말 삭제하시겠습니까?(Y/N): ").strip().upper()
    if confirm == 'Y':
        print("\n삭제하는 중 . . .")
        
        # 원본 데이터 리스트에서 해당 항목 제거
        original_data_list[:] = [item for item in original_data_list if item['idx'] != target_item['idx']]
        
        save_ledger_data(user_id, original_data_list)
        total_asset = calculate_total_asset(original_data_list)
        
        print("--------------------------------------------------------------")
        print("삭제가 완료되었습니다.")
        print(f"현재 ID님의 총 자산은 ₩{total_asset:,}입니다.")
        print("--------------------------------------------------------------")
        return True
    else:
        print("입력을 취소합니다. 주 프롬프트로 돌아갑니다.")
        return True
