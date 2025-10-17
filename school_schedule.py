import tkinter as tk # tkinter라이브러리를 tk로 불러옴
from tkinter import ttk # ttk모듈 불러옴

# 상수 설정
WINDOW_WIDTH = 600 # 창 가로 길이
WINDOW_HEIGHT = 400 # 창 세로 길이

# Tkinter 기본 설정
root = tk.Tk() # 메인 창을 생성
root.title("학교 일정 관리 앱") # 창 이름
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}") # 창 크기 설정

notebook = ttk.Notebook(root) # root 창 안에 Notebook(탭 컨테이너) 생성
notebook.pack(expand=True, fill='both') # 창 크기에 맞게 자동 확장

tab_timetable = ttk.Frame(notebook) # 시간표 탭용 프레임 생성
notebook.add(tab_timetable, text="시간표") # 탭에 프레임 연결,이름 지정
root.mainloop() # 메인 루프