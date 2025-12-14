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


def cinput() -> list[str]:
    """다중 카테고리 입력 → 내부 코드 변환 → 표준명 반환"""
    category_map = get_category_map()
    print("카테고리 목록")
    print(" ", list(category_map.keys()), "\n")

    while True:
        raw = input("카테고리를 입력하세요 (여러 개는 ,로 구분): ")
        raw_list = [c.strip() for c in raw.split(',') if c.strip()]

        codes = convert_names_to_codes(raw_list)
        if not codes:
            print("올바른 카테고리를 입력해야 합니다.")
            continue

        names = convert_codes_to_names(codes)
        print("선택된 카테고리:", names)
        print(SEPERATOR1)
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


def minput() -> list[str]:
    """
    결제수단 입력 → 내부 코드 변환 → 표준명 리스트 반환
    """
    payment_map = get_payment_map()

    print("결제수단 목록")
    print(" ", list(payment_map.keys()), "\n")

    while True:
        method = input("결제수단 입력: ").strip()
        raw_list = [method]  # 단일 입력이지만 리스트 형태로 처리

        # 1) 내부 코드 변환
        codes = convert_names_to_codes(raw_list)
        if not codes:
            print("올바른 결제수단을 입력해야 합니다.")
            continue

        # 2) 표준명 변환
        names = convert_codes_to_names(codes)

        print("선택된 결제수단:", names)
        print(SEPERATOR1)
        return names



def hsave(user_id, date, type, amount, category_list, method_list):
    """파일 저장 + 자산 계산"""
    category_str = ",".join(category_list)
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

                    # 기존 자산 계산
                    total = 0
                    for line in lines:
                        parts = line.split()
                        if parts[1] == 'E':
                            total -= int(parts[2])
                        else:
                            total += int(parts[2])

                    origin_total = total

                    # 새 금액 반영
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
