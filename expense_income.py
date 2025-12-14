import sys
import os
import datetime
import re
from pathlib import Path

from category import convert_codes_to_names, convert_names_to_codes, get_category_map, get_payment_map

# 홈 경로 설정
HOME_DIR = Path.cwd()
LEDGER_FILE_SUFFIX = "_HL.txt"
SEPERATOR1 = '--------------------------------------------------------------'
SEPERATOR2 = '=============================================================='


def valid_date(date_str):
    """날짜 유효성 검사"""
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_str):
        print("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")
        return 0
    try:
        y, m, d = map(int, date_str.split('-'))
        date_obj = datetime.date(y, m, d)
    except ValueError:
        print("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")
        return 0
    if y > 2099 or y < 1900:
        print("날짜는 YYYY-MM-DD 형식으로 입력해야합니다.")
        return 0
    if date_obj > datetime.date.today():
        print("오늘 이후의 날짜는 입력할 수 없습니다.")
        return 0
    return 1


def dinput():
    while True:
        date = input('날짜 입력(YYYY-MM-DD): ')
        print(SEPERATOR1)
        if valid_date(date):
            return date

def cinput():
    """
    사용자에게 카테고리를 입력받아 표준화된 카테고리명 리스트를 반환한다.
    """
    category_map = get_category_map()

    # 1. 사용자 정의 카테고리 목록 출력
    print("\n=== 사용 가능한 카테고리 목록 ===")
    for std, info in category_map.items():
        syns = ", ".join(info['synonyms'])
        print(f"- {std} (동의어: {syns})")

    while True:
        # 2. 사용자 입력
        category = input("\n카테고리를 입력하세요 (여러 개는 ,로 구분): ").strip()

        # 3. split
        name_list = [c.strip() for c in category.split(',')]

        # 4. 이름 → 내부 코드 변환
        codes = convert_names_to_codes(name_list)
        if codes is None:
            print("❌ 카테고리 입력이 잘못되었습니다. 다시 입력해주세요.")
            continue

        # 5. 내부 코드 → 표준명 변환
        names = convert_codes_to_names(codes)
        return names


def ainput():
    while True:
        amount = input('금액 입력: ')
        if not amount.isdecimal():
            print("금액은 정수로 입력해야 합니다.")
        elif amount.startswith('0'):
            print("금액은 선행 0이 아닌 정수로 입력해야 합니다.")
        elif int(amount) <= 0:
            print("금액은 양의 정수로 입력해야 합니다.")
        elif int(amount) > 999999999:
            print("금액은 999,999,999 이하의 값만 허용됩니다.")
        else:
            print(SEPERATOR1)
            return amount


# expense_income.py

from category import (
    get_payment_map,
    convert_names_to_codes,
    convert_codes_to_names
)

def minput():
    """
    사용자에게 결제수단을 입력받아 '표준명' 하나를 리스트로 감싸서 반환.
    예: ['현금'], ['카드']
    """
    payment_map = get_payment_map()

    print("\n=== 사용 가능한 결제수단 목록 ===")
    for std, info in payment_map.items():
        syns = ", ".join(info['synonyms'])
        print(f"- {std} (동의어: {syns})")

    while True:
        method = input("\n결제수단을 입력하세요: ").strip()

        found = None
        # 표준명 매칭
        for std, info in payment_map.items():
            if method == std or method in info['synonyms']:
                found = std
                break

        if found is None:
            print("❌ 결제수단 입력이 잘못되었습니다. 다시 입력해주세요.")
            continue

        # 표준명 리스트로 반환 (hsave에서 join해서 쓰기 위해)
        return [found]
    

#얘가 카테고리를 코드로 변환해서 저장해야되는데ㅠㅠ
def hsave(user_id, date, type, amount, category_list, method_list):
    from category import convert_names_to_codes

    # ✅ category_list가 문자열로 들어오는 경우 방지
    if isinstance(category_list, str):
        category_list = [category_list]

    # ✅ 코드 변환
    category_codes = convert_names_to_codes(category_list)
    print("[디버그] hsave category_list:", category_list)
    print("[디버그] hsave category_codes:", category_codes)

    # ✅ 변환 실패 → 저장 중단
    if not category_codes:
        print("카테고리 코드 변환 실패. 저장할 수 없습니다.")
        return False

    category_str = " ".join(category_codes)
    method_str = ",".join(method_list)

    while True:
        yn = input("\n이대로 저장하시겠습니까?(Y/N): ").lower()
        print("")

        if yn == 'y':
            ledger_file_name = f"{user_id}{LEDGER_FILE_SUFFIX}"
            ledger_file_path = HOME_DIR / ledger_file_name

            try:
                with open(ledger_file_path, 'a+', encoding='utf-8') as f:
                    f.seek(0)
                    lines = [line for line in f.readlines() if line.strip()]
                    f.seek(0, 2)

                    total = 0
                    for line in lines:
                        parts = line.split('\t')
                        if parts[1] == 'E':
                            total -= int(parts[2])
                        else:
                            total += int(parts[2])

                    origin_total = total

                    if type == 'I':
                        total += int(amount)
                    else:
                        total -= int(amount)

                    if total < 0:
                        print(SEPERATOR1)
                        print("현재 지출이 수입보다 커집니다.")
                        print(f"현재 {user_id}님의 총 자산은 ₩{origin_total}입니다.")
                        print(SEPERATOR1)
                        return False

                    # ✅ 코드로 저장
                    f.write(f"{date}\t{type}\t{amount}\t{category_str}\t{method_str}\n")

            except Exception as e:
                print(f"!치명적오류: 파일 처리 중 오류 발생: {e}")
                sys.exit()

            print("\n저장이 완료되었습니다.")
            print(f"현재 ID님의 총 자산은 ₩{total}입니다.")
            print(SEPERATOR1)
            return True

        elif yn == 'n':
            print("입력을 취소합니다.")
            print(SEPERATOR2)
            return True

def expenditure(user_id):
    type = 'E'
    print("")
    date = dinput()
    category = cinput()
    amount = ainput()
    method = minput()

    category_str = ",".join(category)
    method_str = ",".join(method)

    print("날짜         지출    수입    카테고리    결제수단")
    print(f"{date}   {amount}    -      {category_str}        {method_str}")

    while not hsave(user_id, date, type, amount, category, method):
        amount = ainput()
        print(f"{date}   {amount}    -      {category_str}        {method_str}")


def income(user_id):
    type = 'I'
    print("")
    date = dinput()

    # 입금도 convert 기반으로 통일
    category = convert_codes_to_names(convert_names_to_codes(['입금']))

    amount = ainput()
    method = minput()

    category_str = ",".join(category)
    method_str = ",".join(method)

    print("날짜         지출    수입    카테고리    결제수단")
    print(f"{date}     -     {amount}     {category_str}        {method_str}")

    hsave(user_id, date, type, amount, category, method)
