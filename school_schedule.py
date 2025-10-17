import tkinter as tk # tkinter라이브러리를 tk로 불러옴

WINDOW_WIDTH = 600 # 창 가로 길이
WINDOW_HEIGHT = 400 # 창 세로 길이

root = tk.Tk() # 메인 창을 생성
root.title("학교 일정 관리 앱") # 창 이름
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}") # 창 크기 설정

root.mainloop() # 메인 루프