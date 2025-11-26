import sys
import os
import subprocess
from fileCheck import verify_files
from logIn import load_user_info, login

def main_menu():
    while True:
        if(not verify_files()) : continue
        print("\n=메인 메뉴=\n")
        print("[회원가입] [로그인] [종료]\n")
        choice = input("메뉴를 입력하세요: ").strip()

        if choice == "회원가입":
            try:
                script_path = os.path.join(os.path.dirname(__file__), "logIn.py")
                subprocess.run(["python", script_path], check=True)
            except Exception as e:
                print(f"회원가입 실행 중 오류 발생: {e}")
        elif choice == "로그인":
            users = load_user_info()
            login(users)
        elif choice == "종료":
            print("프로그램을 종료합니다.")
            sys.exit()
        else:
            print("입력이 올바르지 않습니다. 다시 입력해주세요.")

if __name__ == "__main__":
    main_menu()