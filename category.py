import os
from pathlib import Path

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
