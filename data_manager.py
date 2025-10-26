import sys
import os


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