import tkinter as tk # tkinter라이브러리를 tk로 불러옴
from tkinter import ttk # ttk모듈 불러옴

# 상수 설정
WINDOW_WIDTH = 600 # 창 가로 길이
WINDOW_HEIGHT = 400 # 창 세로 길이

# Tkinter 기본 설정
root = tk.Tk() # 메인 창을 생성
root.title("학교 일정 관리 앱") # 창 이름
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}") # 창 크기 설정

# Notebook (텝 컨테이너)
notebook = ttk.Notebook(root) # root 창 안에 Notebook(탭 컨테이너) 생성
notebook.pack(expand=True, fill='both') # 창 크기에 맞게 자동 확장

# 시간표 탭
tab_timetable = ttk.Frame(notebook) # 시간표 탭용 프레임 생성
notebook.add(tab_timetable, text="시간표") # 탭에 프레임 연결,이름 지정

# 월~금 버튼 배치
days = ["월", "화", "수", "목", "금"] # 리스트에 요일 저장

for i, day in enumerate(days): # i에는 1~4, day에는 "월"~"금" 저장
    button = ttk.Button(tab_timetable, text=day) # 버튼 생성
    button.grid(row=0, column=i, padx=5, pady=10, sticky="nsew") # 버튼 세팅

# 창 크기에 따라 가로로 늘어가게 함
for i in range(len(day)):
    tab_timetable.columnconfigure(i, weight=1)

root.mainloop() # 메인 루프