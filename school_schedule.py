import tkinter as tk # tkinter라이브러리를 tk로 불러옴
from tkinter import ttk # ttk모듈 불러옴
from tkinter import messagebox # messagebox모듈 불러옴
import json # json라이브러리 불러옴
import os # os라이브러리를 파일 존재 여부 확인용으로 불러옴
from datetime import datetime # 시간 라이브러리 불러옴

# 상수 설정
WINDOW_WIDTH = 550 # 창 가로 길이
WINDOW_HEIGHT = 350 # 창 세로 길이
ITEM_WIDTH = 300 # 준비물 창 가로 길이
ITEM_HEIGHT = 200 # 준비물 창 세로 길이
BUTTON_SIZE = 5 # 버튼 크기
BUTTON_X_BLANK = 1 # 버튼 좌우 여백
BUTTON_Y_BLANK = 1 # 버튼 위아래 여백

# 앱 데이터 전용 폴더
APPDATA_DIR = os.path.join(os.environ['USERPROFILE'], "AppData", "Local", "MyshoolApp")
os.makedirs(APPDATA_DIR, exist_ok=True) # 폴더 없으면 생성
DATA_PATH = os.path.join(APPDATA_DIR, "timetable.json") # 저장 파일 경로 설정
TMP_PATH = os.path.join(APPDATA_DIR, "timetable_temp.json") # 임시 파일 경로
SCHEDULE_DDAY_PATH = os.path.join(APPDATA_DIR, "schedule_dday.json")

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
    
    def update_scrollregion_frame():
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
        canvas.after_idle(update_scrollregion_frame)
    
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
    
    def on_content_change(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollable_frame.bind("<Configure>", on_content_change)
    
    # container와 scrollable_frame을 반환
    return container, scrollable_frame, canvas

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

# 요일 한국어 변환 함수
def get_korean_week():
    week = ["일", "월", "화", "수", "목", "금", "토"] # 요일 저장 리스트
    return week[int(datetime.today().strftime("%w"))]

# 시간표 클래스
class TimeTableManager:
    def __init__(self, root, notebook):
        # 상태 및 데이터 초기화
        self.root = root
        self.notebook = notebook
        self.timetable_data = {"월": [], "화": [], "수": [], "목": [], "금": []} # 요일별 수업 딕셔너리
        self.day_buttons ={} # 요일 버튼 객체를 저장할 딕셔너리
        self.current_selected_button = None # 현재 선택된 버튼 객체를 저장할 변수
        self.item_window = {} # 준비물 창 관리 딕셔너리
        self.current_day = None # 기본 요일 지정
        self.load_timetable() # 저장된 데이터 로드
        
        today = get_korean_week()
        timetable_week = ["월", "화", "수", "목", "금"]
        
        if today in timetable_week:
            self.current_day = today
        else:
            self.current_day = "월"
    
    # 데이터 관리 메서드
    # 저장용 메서드
    def save_timetable(self):
        with open(TMP_PATH, "w", encoding="utf-8") as f:
            json.dump(self.timetable_data, f, ensure_ascii=False, indent=4)
        os.replace(TMP_PATH, DATA_PATH)
    
    # 불러오기 메서드
    def load_timetable(self):
        if os.path.exists(DATA_PATH):
            try:
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    self.timetable_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.timetable_data = {"월": [], "화": [], "수": [], "목": [], "금": []}
        else:
            self.timetable_data = {"월": [], "화": [], "수": [], "목": [], "금": []}
    
    # 메인 UI 구성 메서드
    def setup(self):
        # 시간표 탭용 프레임 생성
        self.tab_timetable = ttk.Frame(self.notebook) # 시간표 탭용 프레임 생성
        self.notebook.add(self.tab_timetable, text="시간표") # 탭에 프레임 연결,이름 지정
        
        # 월~금 버튼 배치
        days = ["월", "화", "수", "목", "금"] # 리스트에 요일 저장
        for i, day in enumerate(days): # i에는 1~4, day에는 "월"~"금" 저장
            button = tk.Button(self.tab_timetable,
                                text=day,
                                fg="black", # 글씨색 검은색
                                bg="SystemButtonFace", # 배경 시스템 기본
                                relief="flat", # 테두리 평평하게
                                bd=0, # 테두리 없음
                                padx=10,
                                pady=5,
                                command=lambda d=day: self.show_timetable(d)) # 버튼 생성
            button.grid(row=0, column=i, padx=5, pady=(5,2), sticky="nsew") # 버튼 세팅
            self.day_buttons[day] = button
        
        # 스크롤 가능 영역 생성 함수 호출
        self.scroll_container, self.input_frame, self.input_canvas = create_scrollable_frame(self.tab_timetable)
        self.scroll_container.grid(row=1, column=0, columnspan=5, pady=(0,5), sticky="nsew")
        
        # 창 크기에 따라 가로로 늘어가게 함
        for i in range(len(days)):
            self.tab_timetable.columnconfigure(i, weight=1)
            self.tab_timetable.rowconfigure(1, weight=1)
        
        # 초기 요일 표시
        self.show_timetable(self.current_day)
        self.create_input_area()
    
    # 시간표 표시 및 선택 로직
    def show_timetable(self, day):
        # 이전에 선택된 버튼 스타일 초기화
        if self.current_selected_button:
            self.current_selected_button.configure(bg="SystemButtonFace", # 배경시스템 기본색
                                            fg="black", # 글씨 검은색
                                            relief="flat", # 테두리 평평하게
                                            bd=0) # 테두리 없음
        
        # 현재 선택된 버튼 스타일 변경
        new_selected_button = self.day_buttons.get(day)
        if new_selected_button:
            new_selected_button.configure(bg="white",
                                        fg="#0078D7", # 글씨색 파란색
                                        relief="solid", # 실선 테두리
                                        bd=1, # 테두리 두께 1
                                        highlightbackground="#0078D7",
                                        highlightcolor="#0078D7")
            self.current_selected_button = new_selected_button
        
        self.current_day = day # 현재 선택된 요일 저장
        self.create_input_widgets() # 함수 호출
    
    # 수업 리스트 표시 메서드
    def create_input_widgets(self):
        # 기존 위젯 제거
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        # 수업 입력 Entry 및 추가 버튼 생성
        self.create_input_area()
        
        # 수업 리스트 표시
        self.display_class_list()
        
        # 스크롤 영역 갱신
        self.input_frame.update_idletasks()
        self.input_canvas.configure(scrollregion=self.input_canvas.bbox("all"))
    
    # 수업 입력창 생성 메서드
    def create_input_area(self):
        # 수업 입력 Entry 생성
        self.entry = ttk.Entry(self.input_frame, width=30)
        self.entry.grid(row=0, column=0, padx=5, pady=5)
        # 플레이스홀더 텍스트 추가
        self.entry.insert(0, "수업 이름") # 기본 문구
        self.entry.configure(foreground="gray") # 글씨 색 연하게
        self.entry.bind("<FocusIn>", lambda event: on_focus_in(event, self.entry, "수업 이름"))
        self.entry.bind("<FocusOut>", lambda event: on_focus_out(event, self.entry, "수업 이름"))
        # Enter 키로 추가
        self.entry.bind('<Return>', lambda event: self.add_class(event=event))
        
        # 추가 버튼 생성
        add_btn = ttk.Button(self.input_frame, text="추가", command=lambda: self.add_class())
        add_btn.grid(row=0, column=1, padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK, sticky="w")
    
    # 수업 리스트 표시 함수
    def display_class_list(self, canvas=None):
        day = self.current_day
        
        for i, cls in enumerate(self.timetable_data[day]):
            lbl = ttk.Label(self.input_frame, text=f"{cls['name']} {'—' * (5 - len(cls['name']))} 준비물 : {len(cls['items'])}개")
            lbl.grid(row=i+1, column=0, sticky="ew", padx=10, pady=1)
            # 준비물 추가 버튼
            item_btn = ttk.Button(self.input_frame, text="준비물", width=BUTTON_SIZE, command=lambda c=cls: self.open_item_window(c))
            item_btn.grid(row=i+1, column=1, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
            # 삭제 버튼
            del_btn = ttk.Button(self.input_frame, text="삭제", width=BUTTON_SIZE, command=lambda c=cls: self.delete_class(c))
            del_btn.grid(row=i+1, column=2, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
            # 위로 이동 버튼
            up_btn = ttk.Button(self.input_frame, text="↑", width=BUTTON_SIZE, command=lambda i=i: self.move_class_up(i))
            up_btn.grid(row=i+1, column=3, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
            # 아래로 이동 버튼
            down_btn = ttk.Button(self.input_frame, text="↓", width=BUTTON_SIZE, command=lambda i=i: self.move_class_down(i))
            down_btn.grid(row=i+1, column=4, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
            # 수정 버튼
            edit_btn = ttk.Button(self.input_frame, text="수정", width=BUTTON_SIZE, command=lambda c=cls: self.edit_class(c))
            edit_btn.grid(row=i+1, column=5, sticky="ew" , padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK)
        
        if canvas:
            canvas.configure(scrollregion=canvas.bbox("all"))
    
    # 수업 관리 메서드
    # 수업 이름 추가 메서드
    def add_class(self, class_name=None, event=None):
        day = self.current_day
        entry_widget = self.entry
        
        if class_name is None:
            class_name = entry_widget.get() # class_name 변수에 저장
        
        if not class_name.split() or class_name == "수업 이름":
            on_focus_out(None, entry_widget, "수업 이름")
            entry_widget.focus_set()
            return
        
        self.timetable_data[day].append({"name": class_name, "items": []}) # 딕셔너리에 저장
        self.save_timetable() # 저장
        self.create_input_widgets()
        
        # Entry 초기화 및 포커스
        entry_widget = self.input_frame.winfo_children()[0]
        entry_widget.focus_set()
        #플레이홀더 텍스트 색 복구 방지
        entry_widget.configure(foreground="black")
        entry_widget.delete(0, tk.END)
    
    # 수업 이름 삭제 메서드
    def delete_class(self, class_to_delete):
        day = self.current_day
        if class_to_delete in self.timetable_data[day]:
            self.timetable_data[day].remove(class_to_delete)
            self.save_timetable()
        self.input_frame.update_idletasks()
        self.create_input_widgets()
    
    # 수업 이름 수정 메서드
    def edit_class(self, cls):
        # 기존 위젯 제거
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        # 기존 이름이 있는 Entry
        edit_entry = ttk.Entry(self.input_frame, width=30)
        edit_entry.insert(0, cls["name"]) # 기존 이름 표시
        edit_entry.grid(row=0, column=0, padx=5, pady=5)
        
        # Enter키로 수정
        edit_entry.bind('<Return>', lambda event: self.update_class(cls, edit_entry.get()))
        
        # 수정 완료 버튼
        save_edit_btn = ttk.Button(self.input_frame, text="수정 완료", command=lambda: self.update_class(cls, edit_entry.get()))
        save_edit_btn.grid(row=0, column=1, padx=5, pady=5)
    
    # 수업 이름 수정 후 저장 메서드
    def update_class(self, cls, new_name):
        if new_name.strip(): # 입력값이 비어있지 않을 때
            cls["name"] = new_name # 딕셔너리 안 이름 수정
            self.save_timetable()
        
        self.create_input_widgets()
    
    # 수업 이름 위로 이동 메서드
    def move_class_up(self, index):
        day = self.current_day
        if index > 0:
            self.timetable_data[day][index], self.timetable_data[day][index-1] = self.timetable_data[day][index-1], self.timetable_data[day][index]
            self.save_timetable()
            self.create_input_widgets()
    
    # 수업 이름 아래로 이동 메서드
    def move_class_down(self, index):
        day = self.current_day
        if index < len(self.timetable_data[day])-1:
            self.timetable_data[day][index], self.timetable_data[day][index+1] = self.timetable_data[day][index+1], self.timetable_data[day][index]
            self.save_timetable()
            self.create_input_widgets()
    
    # 준비물 창 관련 메서드
    # 준비물 창 메서드
    def open_item_window(self, class_data):
        class_name = class_data["name"]
        
        # 창이 이미 열려 있으면 재사용
        if class_name in self.item_window and self.item_window[class_name].winfo_exists():
            self.item_window[class_name].lift()
            return
        
        win = tk.Toplevel(self.root)
        win.title(f"{class_name} 준비물")
        
        # root창 크기 갱신
        self.root.update_idletasks()
        
        # root창 위치 및 크기 정보 가져오기
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        # 중앙 위치 계산
        center_x = root_x + (root_width // 2) - (ITEM_WIDTH // 2)
        center_y = root_y + (root_height // 2) - (ITEM_HEIGHT // 2)
        
        # 중앙에 준비물 창 표시
        win.geometry(f"{ITEM_WIDTH}x{ITEM_HEIGHT}+{center_x}+{center_y}")
        
        # 창 중복 문제 막기
        self.item_window[class_name] = win
        
        # 상단 프레임
        top_frame = ttk.Frame(win)
        top_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # 스크롤 가능 함수 호출
        scroll_container, item_frame, item_canvas = create_scrollable_frame(win)
        
        # 스크롤 기능 win에 배치
        scroll_container.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="nsew")
        
        # 준비물 입력 창
        item_entry = ttk.Entry(top_frame)
        item_entry.pack(side=tk.LEFT, expand=True, fill="x")
        
        # 추가 버튼
        add_btn = ttk.Button(top_frame, text="추가", command=lambda: self.add_item(class_data, item_entry, item_frame, item_canvas))
        add_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Enter키로 추가
        item_entry.bind('<Return>', lambda event: self.add_item(class_data, item_entry, item_frame, item_canvas))
        
        # 플레이홀더 텍스트 추가
        item_entry.insert(0, "준비물") # 기본 문구
        item_entry.configure(foreground="gray") # 글씨 색 연하게
        
        item_entry.bind("<FocusIn>", lambda event: on_focus_in(event, item_entry, "준비물"))
        item_entry.bind("<FocusOut>", lambda event: on_focus_out(event, item_entry, "준비물"))
        
        # 창 크기에 따라 크기 변경
        win.columnconfigure(0, weight=1)
        win.rowconfigure(1, weight=1)
        
        self.refresh_item_list(class_data, item_frame, item_canvas)
        
        # 최소 크기 설정
        win.update()
        win.minsize(win.winfo_width(), win.winfo_height())
        
        # item_window 딕셔너리 정리
        win.protocol("WM_DELETE_WINDOW", lambda: self.close_item_window(class_name, win))
    
    # 준비물 창 닫을 때 정리 메서드
    def close_item_window(self, class_name, win):
        if class_name in self.item_window:
            del self.item_window[class_name]
        win.destroy()
    
    # 준비물 추가 메서드
    def add_item(self, cls, entry_widget, item_frame, item_canvas):
        item_name = entry_widget.get()
        if item_name.strip() and item_name != "준비물": # 입력값이 비어있지 않을 때
            cls["items"].append(item_name) # 딕셔너리에 추가
            self.save_timetable() # 저장
            self.refresh_item_list(cls, item_frame, item_canvas)
            
            try:
                entry_widget.delete(0, tk.END)
            except tk.TclError:
                pass
            entry_widget.focus_set()
            #플레이홀더 텍스트 색 복구 방지
            entry_widget.configure(foreground="black")
        else:
            entry_widget.focus_set()
        self.create_input_widgets()
    
    # 준비물 삭제 메서드
    def delete_item(self, cls, item_name, item_frame, item_canvas):
        cls["items"].remove(item_name)
        self.save_timetable()
        self.refresh_item_list(cls, item_frame, item_canvas)
        
        # 함수 호출(UI 갱신)
        self.create_input_widgets()
    
    # 준비물 목록 갱신 메서드
    def refresh_item_list(self, cls, item_frame, item_canvas):
        # 기존 위젯 제거
        for widget in item_frame.winfo_children():
            widget.destroy()
        
        # 준비물 Label + 삭제 버튼 생성
        for i, item in enumerate(cls["items"]):
            lbl = ttk.Label(item_frame, text=item)
            lbl.grid(row=i, column=0, sticky="w", padx=5)
            
            del_btn = ttk.Button(item_frame, text="삭제", command=lambda it=item: self.delete_item(cls, it, item_frame, item_canvas))
            del_btn.grid(row=i, column=1, padx=5)
        
        # 스크롤 영역 갱신
        item_canvas.after_idle(lambda: item_canvas.configure(scrollregion=item_canvas.bbox("all")))

class ScheduleDDay():
    # 상태 및 데이터 초기화
    def __init__(self, root, notebook):
        self.root = root
        self.notebook = notebook
        self.schedule_dday = {} # 일정 날짜 저장 딕셔너리
        self.today = datetime.today()
        self.load_schedule_dday()
    
    # 데이터 저장
    def save_schedule_dday(self):
        with open(SCHEDULE_DDAY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.schedule_dday, f, ensure_ascii=False, indent=4)
    
    # 데이터 불러오기
    def load_schedule_dday(self):
        if os.path.exists(SCHEDULE_DDAY_PATH):
            try:
                with open(SCHEDULE_DDAY_PATH, "r", encoding="utf-8") as f:
                    self.schedule_dday = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.schedule_dday = {}
        else:
            self.schedule_dday = {}
    
    # 메인 UI 구성 메서드
    def setup(self):
        # 일정 d-day 탭용 프레임 생성
        self.tab_dday = ttk.Frame(self.notebook) #  일정 날짜 탭용 프레임 생성
        self.notebook.add(self.tab_dday, text="D-day") # 탭에 프레임 연결,이름 지정
        
        # 스크롤 가능한 영역 생성
        self.scroll_container, self.input_frame, self.input_canvas = create_scrollable_frame(self.tab_dday)
        self.scroll_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0, 5))
        
        self.tab_dday.grid_rowconfigure(0, weight=1)
        self.tab_dday.grid_columnconfigure(0, weight=1)
        
        # 입력창 생성
        self.to_day()
        self.create_input_area()
        self.display_schedule_list()
        
        self.notebook.bind("<<NotebookTabChanged>>", lambda event: self.tab_dday.focus_set() if self.notebook.select() == str(self.tab_dday) else None)
    
    # 오늘 날짜 표시 메서드
    def to_day(self):
        self.week_korean = get_korean_week()
        
        self.label = ttk.Label(self.input_frame, text=f'{self.today.strftime("%Y %m/%d")} {self.week_korean}요일', font="Arial")
        self.label.grid(row=0, column=0, padx=0, pady=0, columnspan=2, sticky="w")
    
    # 일정 이름 및 날짜 입력창 생성 메서드
    def create_input_area(self):
        # 일정 이름 Entry 생성
        self.entry = ttk.Entry(self.input_frame, width=30)
        self.entry.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        # 플레이스홀더 텍스트 추가
        self.entry.insert(0, "일정 이름") # 기본 문구
        self.entry.configure(foreground="gray") # 글씨 색 연하게
        self.entry.bind("<FocusIn>", lambda event: on_focus_in(event, self.entry, "일정 이름"))
        self.entry.bind("<FocusOut>", lambda event: on_focus_out(event, self.entry, "일정 이름"))
        
        # 날짜 Entry 생성
        self.entry_data = ttk.Entry(self.input_frame, width=15)
        self.entry_data.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        # 플레이스홀더 텍스트 생성
        self.entry_data.insert(0, "YYYY-MM-DD") # 기본 문구
        self.entry_data.configure(foreground="gray") # 글씨 색 연하게
        self.entry_data.bind("<FocusIn>", lambda event: on_focus_in(event, self.entry_data, "YYYY-MM-DD"))
        self.entry_data.bind("<FocusOut>", lambda event: on_focus_out(event, self.entry_data, "YYYY-MM-DD"))
        
        # Enter 키로 추가
        self.entry.bind('<Return>', lambda event: self.add_schedule())
        self.entry_data.bind('<Return>', lambda event: self.add_schedule())
        # 추가 버튼 생성
        add_btn = ttk.Button(self.input_frame, text="추가", command=lambda: self.add_schedule())
        add_btn.grid(row=1, column=2, padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK, sticky="w")
    
    # 일정 목록 표시 메서드
    def display_schedule_list(self):
        # 기존 표시 위젯 제거
        for widget in self.input_frame.grid_slaves():
            if int(widget.grid_info()["row"]) >= 2:
                widget.destroy()
        
        # D-day 기준으로 정렬
        sorted_schedules = sorted(
            self.schedule_dday.items(),
            key=lambda x: (datetime.strptime(
                "-".join([p.zfill(2) for p in x[1].split("-")]), "%Y-%m-%d") - datetime.today()).days
                if x[1] else float('inf')
        )
        
        for i, (schedule_name, schedule_date) in enumerate(sorted_schedules ):
            # d-day 계산
            if schedule_date:
                schedule_day = datetime.strptime(schedule_date, "%Y-%m-%d")
                dday = (schedule_day - datetime.today()).days+1
                if dday > 0:
                    text = f"{schedule_name}<{schedule_date}> - D-{dday}"
                elif dday == 0:
                    text = f"{schedule_name}<{schedule_date}> - D-day"
                elif dday < 0:
                    text = f"{schedule_name}<{schedule_date}> - 끝({dday}day)"
            else:
                text = f"{schedule_name} - 날짜 미입력"
            
            # 일정 이름 및 날짜 표시
            lbl = ttk.Label(self.input_frame, text=text)
            lbl.grid(row=i+2, column=0, sticky="w", padx=5, pady=2)
            
            # 삭제 버튼
            del_btn = ttk.Button(self.input_frame, text="삭제", command=lambda key=schedule_name: self.delete_schedule(key))
            del_btn.grid(row=i+2, column=1, padx=BUTTON_X_BLANK, pady=BUTTON_Y_BLANK, sticky="w")
    
    # 일정 이름 및 날짜 추가 메서드
    def add_schedule(self, schedule_name=None, schedule_date=None, event=None):
        schedule_name = self.entry.get().strip()
        schedule_date = self.entry_data.get().strip()
        
        # 일정 이름 입력 값 확인
        if not schedule_name or schedule_name == "시험 이름":
            on_focus_out(None, self.entry, "시험 이름")
            self.entry.focus_set()
            return
        
        # 일정 날짜 입력 값 확인
        if not schedule_date or schedule_date == "YYYY-MM-DD":
            on_focus_out(None, self.entry_data, "YYYY-MM-DD")
            self.entry_data.focus_set()
            return
        
        # 일정 날짜 형식 확인
        try:
            schedule_day = datetime.strptime(schedule_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("날짜 오류", "날짜를 YYYY-MM-DD 형식으로 입력하세요.")
            self.entry_data.focus_set()
            return
        
        # 일정 이름 추가
        if schedule_name not in self.schedule_dday:
            self.schedule_dday[schedule_name] = schedule_date
            self.save_schedule_dday()
        else:
            self.schedule_dday[schedule_name] = schedule_date
            self.save_schedule_dday()
        
        
        # UI 업데이트
        self.display_schedule_list()
        
        # 입력창 초기화
        self.entry.delete(0, tk.END)
        self.entry_data.delete(0, tk.END)
        on_focus_out(None, self.entry_data, "YYYY-MM-DD")
        self.entry.focus_set()
    
    # 일정 삭제 메서드
    def delete_schedule(self, schedule_key):
        if schedule_key in self.schedule_dday:
            del self.schedule_dday[schedule_key]
            self.save_schedule_dday()
            self.create_input_area()
            self.display_schedule_list()

# 스타일 함수
def set_styles():
    style = ttk.Style()
    
    # 테마 설정
    try:
        style.theme_use('vista')
    except tk.TclError:
        pass
    # Notebook 스타일
    style.configure("TNotebook.Tab",
                    padding=[10, 5],
                    background="lightgray", # 배경색 회색
                    foreground="black") # 글씨 색 검은색
    # 선택되었을 때
    style.map("TNotebook.Tab",
            background=[("selected", "white")], # 배경 흰색
            foreground=[("selected", "#0078D7")]) # 글씨 파란색

# 메인 애플리케이션 실행
if __name__ == "__main__":
    # Tkinter 기본 설정
    root = tk.Tk() # 메인 창을 생성
    root.title("학교 일정 관리 앱") # 창 이름
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}") # 창 크기 설정
    
    # 스타일 적용
    set_styles()
    
    # Notebook (텝 컨테이너)
    notebook = ttk.Notebook(root) # root 창 안에 Notebook(탭 컨테이너) 생성
    notebook.pack(expand=True, fill='both') # 창 크기에 맞게 자동 확장
    
    # TimeTableManaher 인스턴스 생성 및 실행
    timetable_manager = TimeTableManager(root, notebook)
    timetable_manager.setup()
    schedule_dday = ScheduleDDay(root, notebook)
    schedule_dday.setup()
    
    root.mainloop() # 메인 루프