import tkinter as tk # tkinter라이브러리를 tk로 불러옴
from tkinter import ttk # ttk모듈 불러옴
import json # json라이브러리 불러옴
import os # os라이브러리를 파일 존재 여부 확인용으로 불러옴

# 상수 설정
WINDOW_WIDTH = 600 # 창 가로 길이
WINDOW_HEIGHT = 400 # 창 세로 길이

ITEM_WIDTH = 300 # 준비물 창 가로 길이
ITEM_HEIGHT = 200 # 준비물 창 세로 길이

BUTTON_SIZE = 5 # 버튼 크기
BUTTON_X_BLANK = 1 # 버튼 좌우 여백
BUTTON_Y_BLANK = 1 # 버튼 위아래 여백

# 요일별 수업 딕셔너리
timetable_data = {"월": [], "화": [], "수": [], "목": [], "금": []}

# 스크롤 가능한 프레임 생성 함수
def create_scrollable_frame(parent):
    container = ttk.Frame(parent)
    
    # 컨테이너의 크기 조절
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    
    # Canvas와 Scrollbar 생성
    canvas = tk.Canvas(container)
    scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    
    # Canvas에 Scrollbar 연결
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    
    # Canvas와 Scrollbar 배치
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")
    
    # 위젯이 올라갈 스크롤 프레임
    scrollable_frame = ttk.Frame(canvas)
    
    # ID 저장
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    def update_scrollregion():
            # 모든 위젯의 실제 크기 반영
            scrollable_frame.update_idletasks()
            
            # scrollregion 갱신 (전체 영역)
            bbox = canvas.bbox("all")
            if bbox: # bbox가 None일 때 오류 방지
                canvas.configure(scrollregion=bbox)
            
            # 현재 프레임 캔버스의 실제 크기 비교 변수
            frame_width = scrollable_frame.winfo_reqwidth()
            frame_height = scrollable_frame.winfo_reqheight()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            # 수평 Scrollbar 보이기/숨기기
            if frame_width > canvas_width:
                scrollbar_x.grid(row=1, column=0, sticky="ew")
            else:
                scrollbar_x.grid_remove()
            
            # 수직 Scrollbar 보이기/숨기기
            if frame_height > canvas_height:
                scrollbar_y.grid(row=0, column=1, sticky="ns")
            else:
                scrollbar_y.grid_remove()
            
            # 캔버스 내부 프레임 폭 자동 조절
            canvas.itemconfig(frame_id, width=max(canvas_width, scrollable_frame.winfo_reqwidth()))
    
    # 스크롤 영역 자동 갱신
    def on_frame_configure(event=None):
        canvas.after_idle(update_scrollregion)
    
    canvas.bind("<Configure>", on_frame_configure)
    
    # 마우스 휠로 스크롤하는 함수
    def _on_mousewheel(event):
        # 현재 프레임 캔버스의 실제 크기 비교 변수
        frame_height = scrollable_frame.winfo_reqheight()
        canvas_height = canvas.winfo_height()
        if hasattr(event, 'delta'): # Windows
            if event.state & 0x1: # Shift 키 눌렀을 때
                if canvas.bbox("all")[2] > canvas.winfo_width(): # 전체 폭 > 캔버스 폭
                    canvas.xview_scroll(int(-1 * event.delta / 120), "units") # 가로 스크롤
            else: # 그냥 휠일때
                if canvas.bbox("all")[3] > canvas.winfo_height(): # 전체 높이 > 캔버스 높이
                    canvas.yview_scroll(int(-1 * event.delta / 120), "units") # 세로 스크롤
        elif event.num == 4: # Linux, 위로
            if frame_height > canvas_height:
                canvas.yview_scroll(-1, "units")
        elif event.num == 5: # Linux, 아래로
            if frame_height > canvas_height:
                canvas.yview_scroll(1, "units")
    
    # 캔버스에 마우스 들어왔을 때 바인딩
    def bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel) # Windows
        canvas.bind_all("<Button-4>", _on_mousewheel) # Linux 위로
        canvas.bind_all("<Button-5>", _on_mousewheel) # Linux 아래로
    
    # 캔버스에서 마우스 나갔을 때 언바인딩
    def unbind_mousewheel(event):
        canvas.unbind("<MouseWheel>")
        canvas.unbind("<Button-4>")
        canvas.unbind("<Button-5>")
    
    canvas.bind("<Enter>", bind_mousewheel)
    canvas.bind("<Leave>", unbind_mousewheel)
    
    # container와 scrollable_frame을 반환
    return container, scrollable_frame, canvas

# 저장용 함수
def save_timetable():
    tmp_file = "timetable_tem.json"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(timetable_data, f, ensure_ascii=False, indent=4)
    os.replace(tmp_file, "timetable.json")

# 불러오기 함수
def load_timetable():
    global timetable_data
    if os.path.exists("timetable.json"):
        try:
            with open("timetable.json", "r", encoding="utf-8") as f:
                timetable_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            timetable_data = {"월": [], "화": [], "수": [], "목": [], "금": []}

# 입력창 클릭시 플레이홀더를 사라지게 하는 함수
def on_focus_in(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.configure(foreground="black")

# 입력창이 비어 있을시 플레이홀더 문구 표시 함수
def on_focus_out(event, entry, placeholder):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.configure(foreground="gray")

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
    
    # 추가 버튼 생성
    add_btn = ttk.Button(input_frame, text="추가", command=lambda: add_class(day, entry.get()))
    add_btn.grid(row=0, column=1, padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK, sticky="w")
    
    # 플레이스홀더 텍스트 추가
    entry.insert(0, "수업 이름") # 기본 문구
    entry.configure(foreground="gray") # 글씨 색 연하게
    entry.bind("<FocusIn>", lambda event: on_focus_in(event, entry, "수업 이름"))
    entry.bind("<FocusOut>", lambda event: on_focus_out(event, entry, "수업 이름"))
    
    # 저장된 수업들을 Label로 표시
    for i, cls in enumerate(timetable_data[day]):
        lbl = ttk.Label(input_frame, text=f"{cls['name']} {'—' * (5 - len(cls['name']))} 준비물 : {len(cls['items'])}개")
        lbl.grid(row=i+1, column=0, sticky="ew", padx=10, pady=1)
        # 준비물 추가 버튼
        item_btn = ttk.Button(input_frame, text="준비물", width=BUTTON_SIZE, command=lambda c=cls: open_item_window(day, c))
        item_btn.grid(row=i+1, column=1, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
        # 삭제 버튼
        del_btn = ttk.Button(input_frame, text="삭제", width=BUTTON_SIZE, command=lambda c=cls: delete_class(day,c))
        del_btn.grid(row=i+1, column=2, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
        # 위로 이동 버튼
        up_btn = ttk.Button(input_frame, text="↑", width=BUTTON_SIZE, command=lambda i=i: move_class_up(day,i))
        up_btn.grid(row=i+1, column=3, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
        # 아래로 이동 버튼
        down_btn = ttk.Button(input_frame, text="↓", width=BUTTON_SIZE, command=lambda i=i: move_class_down(day,i))
        down_btn.grid(row=i+1, column=4, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
        # 수정 버튼
        edit_btn = ttk.Button(input_frame, text="수정", width=BUTTON_SIZE, command=lambda c=cls: edit_class(day, c))
        edit_btn.grid(row=i+1, column=5, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
    
    input_frame.update_idletasks()
    input_canvas.configure(scrollregion=input_canvas.bbox("all"))
    
    try:
        input_canvas.after_idle(lambda: input_canvas.configure(scrollregion=input_canvas.bbox("all")))
    except NameError:
        pass
    
    return entry

# 수업 이름 추가 함수
def add_class(day, class_name=None, event=None):
    if class_name is None:
        entry_widget = input_frame.winfo_children()[0]
        class_name = entry_widget.get() # class_name 변수에 저장
    
    if class_name.strip() and class_name != "수업 이름": # 입력값이 비어있지 않을 때
        timetable_data[day].append({"name": class_name, "items": []}) # 딕셔너리에 저장
        save_timetable() # 저장
    
    create_input_widgets(day) # 함수 호출
    # Entry 초기화
    entry_widget = input_frame.winfo_children()[0] # 첫 번째 위젯이 Entry
    entry_widget.delete(0, tk.END)
    entry_widget.focus_set()
    
    #플레이홀더 텍스트 색 복구 방지
    entry_widget.configure(foreground="black")

# 수업 이름 삭제 함수
def delete_class(day, class_to_delete):
    if class_to_delete in timetable_data[day]:
        timetable_data[day].remove(class_to_delete)
        save_timetable()
    create_input_widgets(day)

# 수업 이름 수정 함수
def edit_class(day, cls):
    # 기존 위젯 제거
    for widget in input_frame.winfo_children():
        widget.destroy()
    
    # 기존 이름이 있는 Entry
    entry = ttk.Entry(input_frame, width=30)
    entry.insert(0, cls["name"]) # 기존 이름 표시
    entry.grid(row=0, column=0, padx=5, pady=5)
    
    # Enter키로 수정
    entry.bind('<Return>', lambda event: update_class(day, cls, entry.get()))
    
    # 수정 완료 버튼
    save_edit_btn = ttk.Button(input_frame, text="수정 완료", command=lambda: update_class(day, cls, entry.get()))
    save_edit_btn.grid(row=0, column=1, padx=5, pady=5)

# 수업 이름 수정 후 저장 함수
def update_class(day, cls, new_name):
    if new_name.strip(): # 입력값이 비어있지 않을 때
        cls["name"] = new_name # 딕셔너리 안 이름 수정
        save_timetable()
    
    create_input_widgets(day) # 함수 호출

# 수업 이름 위로 이동 함수
def move_class_up(day, index):
    if index > 0:
        timetable_data[day][index], timetable_data[day][index-1] = timetable_data[day][index-1], timetable_data[day][index]
        save_timetable()
        create_input_widgets(day)

# 수업 이름 아래로 이동 함수
def move_class_down(day, index):
    if index < len(timetable_data[day])-1:
        timetable_data[day][index], timetable_data[day][index+1] = timetable_data[day][index+1], timetable_data[day][index]
        save_timetable()
        create_input_widgets(day)

item_window = {}

# 준비물 창 함수
def open_item_window(day, class_data):
    class_name = class_data["name"]
    
    # 창이 이미 열려 있으면 재사용
    if class_name in item_window and item_window[class_name].winfo_exists():
        item_window[class_name].lift()
        return
    
    win = tk.Toplevel(root)
    win.title(f"{class_name} 준비물")
    
    # root창 크기 갱신
    root.update_idletasks()
    
    # root창 위치 및 크기 정보 가져오기
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    
    # 중앙 위치 계산
    center_x = root_x + (root_width // 2) - (ITEM_WIDTH // 2)
    center_y = root_y + (root_height // 2) - (ITEM_HEIGHT // 2)
    
    # 중앙에 준비물 창 표시
    win.geometry(f"{ITEM_WIDTH}x{ITEM_HEIGHT}+{center_x}+{center_y}")
    
    # 창 중복 문제 막기
    item_window[class_name] = win
    
    # 상단 프레임
    top_frame = ttk.Frame(win)
    top_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    
    # 스크롤 가능 함수 호출
    scroll_container, item_frame, item_canvas = create_scrollable_frame(win)
    
    # 스크롤 기능 win에 배치
    scroll_container.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="nsew")
    
    # 준비물 입력 창
    entry = ttk.Entry(top_frame)
    entry.pack(side=tk.LEFT, expand=True, fill="x")
    
    # 추가 버튼
    add_btn = ttk.Button(top_frame, text="추가", command=lambda: add_item(day, class_data, entry, item_frame, item_canvas))
    add_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    # Enter키로 추가
    entry.bind('<Return>', lambda event: add_item(day, class_data, entry, item_frame, item_canvas))
    
    # 플레이홀더 텍스트 추가
    entry.insert(0, "준비물") # 기본 문구
    entry.configure(foreground="gray") # 글씨 색 연하게
    
    entry.bind("<FocusIn>", lambda event: on_focus_in(event, entry, "준비물"))
    entry.bind("<FocusOut>", lambda event: on_focus_out(event, entry, "준비물"))
    
    # 창 크기에 따라 크기 변경
    win.columnconfigure(0, weight=1)
    win.rowconfigure(1, weight=1)
    
    refresh_item_list(day, class_data, item_frame, item_canvas)
    
    # 최소 크기 설정
    win.update()
    min_w = win.winfo_width()
    min_h = win.winfo_height()
    win.minsize(min_w, min_h)

# 준비물 창 닫을 때 정리 함수
def close_item_window(class_name, win):
    if class_name in item_window:
        del item_window[class_name]
    win.destroy()

# 준비물 추가 함수
def add_item(day, cls, entry_widget, item_frame, item_canvas):
    item_name = entry_widget.get()
    if item_name.strip() and item_name != "준비물": # 입력값이 비어있지 않을 때
        cls["items"].append(item_name) # 딕셔너리에 추가
        save_timetable() # 저장
        refresh_item_list(day, cls, item_frame, item_canvas)
        entry_widget.delete(0, tk.END)
        
        #플레이홀더 텍스트 색 복구 방지
        entry_widget.configure(foreground="black")
        
        # 함수 호출(UI 갱신)
        create_input_widgets(day)

# 준비물  삭제 함수
def delete_item(day, cls, item_name, item_frame, item_canvas):
    cls["items"].remove(item_name)
    save_timetable()
    refresh_item_list(day, cls, item_frame, item_canvas)
    
    # 함수 호출(UI 갱신)
    create_input_widgets(day)

# 준비물 목록 갱신 함수
def refresh_item_list(day, cls, item_frame, item_canvas):
    # 기존 위젯 제거
    for widget in item_frame.winfo_children():
        widget.destroy()
    
    # 준비물 Label + 삭제 버튼 생성
    for i, item in enumerate(cls["items"]):
        lbl = ttk.Label(item_frame, text=item)
        lbl.grid(row=i, column=0, sticky="w", padx=5)
        
        del_btn = ttk.Button(item_frame, text="삭제", command=lambda it=item: delete_item(day, cls, it, item_frame, item_canvas))
        del_btn.grid(row=i, column=1, padx=5)
    
    # 스크롤 영역 갱신
    item_canvas.after_idle(lambda: item_canvas.configure(scrollregion=item_canvas.bbox("all")))

# 동작 확인용 함수
def show_timetable(day):
    create_input_widgets(day) # 함수 호출

load_timetable() # 함수 호출

# 문자열로 저장된 수업 데이터를 딕셔너리로 변환
for day in timetable_data:
    for i, cls in enumerate(timetable_data[day]):
        if isinstance(cls, str): # cls가 문자열이면
            timetable_data[day][i] = {"name": cls, "items": []} # 딕셔너리로 변환

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

# 스크롤 가능 영역 생성 함수 호출
scroll_container, input_frame, input_canvas = create_scrollable_frame(tab_timetable)
scroll_container.grid(row=1, column=0, columnspan=5, pady=20, sticky="nsew")

# 창 크기에 따라 가로로 늘어가게 함
for i in range(len(days)):
    tab_timetable.columnconfigure(i, weight=1)
    tab_timetable.rowconfigure(1, weight=1)

root.mainloop() # 메인 루프