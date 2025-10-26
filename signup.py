import os

def signup():
    print("\n메뉴를 입력하세요: 회원가입")
    print("----------------------------------------------")
    user_id = input("아이디 입력: ").strip()
    password = input("비밀번호 입력: ").strip()
    password_check = input("비밀번호 확인: ").strip()

    if password != password_check:
        print("오류 메시지: 비밀번호가 일치하지 않습니다.")
        print("회원가입 메뉴로 리턴됩니다.\n")
        return

    if not os.path.exists("user_info.txt"):
        open("user_info.txt", "w", encoding="utf-8").close()

    with open("user_info.txt", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().split("\t", 1)[0] == user_id:
                print("오류 메시지: 이미 사용 중인 아이디입니다.")
                print("회원가입 메뉴로 리턴됩니다.\n")
                return

    with open("user_info.txt", "a", encoding="utf-8") as f:
        f.write(f"{user_id}\t{password}\n")

    ledger_filename = f"{user_id}_HL.txt"
    open(ledger_filename, "a", encoding="utf-8").close()

    print(f"{ledger_filename} 파일이 생성되었습니다.")
    print("회원가입이 완료되었습니다.")
    print("----------------------------------------------\n")

if __name__ == "__main__":
    signup()
