import tkinter as tk # tkinter라이브러리를 tk로 불러옴
from tkinter import ttk # ttk모듈 불러옴
import json # json라이브러리 불러옴
import os # os라이브러리를 파일 존재 여부 확인용으로 불러옴

# 상수 설정
WINDOW_WIDTH = 600 # 창 가로 길이
WINDOW_HEIGHT = 400 # 창 세로 길이

# 요일별 수업 딕셔너리
timetable_data = {"월": [], "화": [], "수": [], "목": [], "금": []}

# 저장용 함수
def save_timetable():
    with open("timetable.json", "w", encoding="utf-8") as f:
        json.dump(timetable_data, f, ensure_ascii=False, indent=4)

# 불러오기 함수
def load_timetable():
    global timetable_data
    if os.path.exists("timetable.json"):
        try:
            with open("timetable.json", "r", encoding="utf-8") as f:
                timetable_data = json.load(f)
        except json.JSONDecodeError:
            timetable_data = {"월": [], "화": [], "수": [], "목": [], "금": []}

# 입력창+버튼 생성 함수
def create_input_widgets(day):
    # input_frame 안의 기존 위젯들 삭제
    for widget in input_frame.winfo_children():
        widget.destroy()
    
    # 수업 입력 Entry 생성
    entry = ttk.Entry(input_frame, width=30)
    entry.grid(row=0, column=0, padx=5, pady=5)
    
    # Enter 키로 추가
    entry.bind('<Return>', lambda event: add_class(day, event=event))
    
    #추가 버튼 생성
    add_btn = ttk.Button(input_frame, text="추가", command=lambda: add_class(day, entry.get()))
    add_btn.grid(row=0, column=1, padx=5, pady=5)
    
    # 저장된 수업들을 Label로 표시
    for i, cls in enumerate(timetable_data[day]):
        lbl = ttk.Label(input_frame, text=cls)
        lbl.grid(row=i+1, column=0, sticky="nsew", padx=5)
        # 삭제 버튼
        del_btn = ttk.Button(input_frame, text="삭제", width=5, command=lambda c=cls: delete_class(day,c))
        del_btn.grid(row=i+1, column=1, sticky="nsew", padx=5)
        # 수정 버튼
        edit_btn = ttk.Button(input_frame, text="수정", width=5, command=lambda c=cls: edit_class(day, c))
        edit_btn.grid(row=i+1, column=2, sticky="nsew", padx=5)
    
    # 창 크기에 따라 버튼 늘어나게 함
    for i in range(3):
        input_frame.columnconfigure(i, weight=1)

    return entry

# 수업 이름 추가 함수
def add_class(day, class_name=None, event=None):
    if class_name is None:
        entry_widget = input_frame.winfo_children()[0]
        class_name = entry_widget.get() #class_name 변수에 저장
    
    if class_name.strip(): # 입력값이 비어있지 않을 때
        timetable_data[day].append(class_name) # 딕셔너리에 저장
        save_timetable() # 저장
    
    create_input_widgets(day) # 함수 호출
    # Entry 초기화
    entry_widget = input_frame.winfo_children()[0] # 첫 번째 위젯이 Entry
    entry_widget.delete(0, tk.END)

# 수업 이름 삭제 함수
def delete_class(day, class_name):
    if class_name in timetable_data[day]:
        timetable_data[day].remove(class_name)
        save_timetable()
    create_input_widgets(day)

# 수업 이름 수정 함수
def edit_class(day, old_name):
    # 기존 위젯 제거
    for widget in input_frame.winfo_children():
        widget.destroy()
    
    # 기존 이름이 있는 Entry
    entry = ttk.Entry(input_frame, width=30)
    entry.insert(0, old_name) # 기존에 있던 수업 이름 입력창에 표시
    entry.grid(row=0, column=0, padx=5, pady=5)
    
    # Enter키로 수정
    entry.bind('<Return>', lambda event: update_class(day, old_name, entry.get()))
    
    # 수정 완료 버튼
    save_edit_btn = ttk.Button(input_frame, text="수정 완료", command=lambda: update_class(day, old_name, entry.get()))
    save_edit_btn.grid(row=0, column=1, padx=5, pady=5)

# 수업 이름 수정 후 저장 함수
def update_class(day, old_name, new_name):
    if new_name.strip(): # 입력값이 비어있지 않을 때
        try:
            index = timetable_data[day].index(old_name)
            timetable_data[day][index] = new_name # 새 이름으로 변경
            save_timetable()
        except ValueError:
            pass # old_name이 없을 경우 대비
    
    create_input_widgets(day) # 함수 호출

# 동작 확인용 함수
def show_timetable(day):
    create_input_widgets(day) # 함수 호출

load_timetable() # 함수 호출

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
    button = ttk.Button(tab_timetable, text=day, command=lambda d=day: show_timetable(d)) # 버튼 생성
    button.grid(row=0, column=i, padx=5, pady=10, sticky="nsew") # 버튼 세팅

# 입력 프레임 생성
input_frame = ttk.Frame(tab_timetable) # tab_timetable 안에 Frame 생성
input_frame.grid(row=1, column=0, columnspan=5, pady=20, sticky="nsew") # 세팅

# 창 크기에 따라 가로로 늘어가게 함
for i in range(len(days)):
    tab_timetable.columnconfigure(i, weight=1)


root.mainloop() # 메인 루프