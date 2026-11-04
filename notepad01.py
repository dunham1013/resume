import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from pathlib import Path


# ---------- 파일 기능 ----------
def update_title():
    name = Path(current_file).name if current_file else "제목 없음"
    root.title(f"{name} - 수업용 메모장")


def save_file():
    global current_file
    path = current_file or filedialog.asksaveasfilename(
        parent=root, title="저장", defaultextension=".txt",
        filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
    )
    if not path:  # 대화상자에서 취소한 경우
        return False
    try:
        # end-1c: Text 위젯이 자동으로 붙이는 마지막 개행은 제외
        Path(path).write_text(text.get("1.0", "end-1c"), encoding="utf-8")
    except (OSError, UnicodeError) as error:
        messagebox.showerror("저장 오류", str(error), parent=root)
        return False
    current_file = path
    text.edit_modified(False)
    update_title()
    return True


def confirm_save():
    if not text.edit_modified():
        return True
    answer = messagebox.askyesnocancel(
        "저장 확인", "변경한 내용을 저장하시겠습니까?", parent=root
    )
    if answer is None:  # 취소: 새파일/열기/종료도 중단
        return False
    return save_file() if answer else True


def new_file():
    global current_file
    if not confirm_save():
        return
    text.delete("1.0", tk.END)
    text.edit_modified(False)
    current_file = None
    update_title()
    update_status()
    text.focus_set()


def open_file():
    global current_file
    if not confirm_save():
        return
    path = filedialog.askopenfilename(
        parent=root, title="열기",
        filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
    )
    if not path:
        return
    try:
        content = Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        messagebox.showerror(
            "열기 오류", f"UTF-8 텍스트 파일을 선택해 주세요.\n{error}", parent=root
        )
        return
    # 읽기에 성공한 뒤에만 기존 내용을 교체
    text.delete("1.0", tk.END)
    text.insert("1.0", content)
    text.edit_modified(False)
    current_file = path
    update_title()
    update_status()
    text.focus_set()


def exit_program():
    if confirm_save():
        root.destroy()


# ---------- 편집 기능 ----------
def cut_text():
    text.focus_set()
    text.event_generate("<<Cut>>")


def copy_text():
    text.focus_set()
    text.event_generate("<<Copy>>")


def paste_text():
    text.focus_set()
    text.event_generate("<<Paste>>")


# ---------- 서식 기능 ----------
def apply_font():
    # 기본 글꼴 크기와 화면 배율을 따로 관리
    actual_size = max(1, round(base_font_size * zoom_percent / 100))
    display_font.configure(size=actual_size)
    update_status()


def change_font():
    dialog = tk.Toplevel(root)
    dialog.title("글꼴")
    dialog.resizable(False, False)
    dialog.transient(root)

    ttk.Label(dialog, text="글꼴").grid(row=0, column=0, padx=10, pady=10)
    family_box = ttk.Combobox(
        dialog, values=sorted(set(tkfont.families(root))), state="readonly", width=28
    )
    family_box.set(display_font.actual("family"))
    family_box.grid(row=0, column=1, padx=10, pady=10)

    ttk.Label(dialog, text="기본 크기(8~72)").grid(row=1, column=0, padx=10, pady=10)
    size_var = tk.StringVar(value=str(base_font_size))
    ttk.Spinbox(dialog, from_=8, to=72, textvariable=size_var, width=8).grid(
        row=1, column=1, padx=10, pady=10, sticky="w"
    )

    def apply_selection():
        global base_font_size
        try:
            size = int(size_var.get())
            if not 8 <= size <= 72:
                raise ValueError
        except ValueError:
            messagebox.showerror("크기 오류", "8~72의 정수를 입력해 주세요.", parent=dialog)
            return
        base_font_size = size
        display_font.configure(family=family_box.get())
        apply_font()
        dialog.destroy()
        text.focus_set()

    ttk.Button(dialog, text="적용", command=apply_selection).grid(
        row=2, column=0, padx=10, pady=10
    )
    ttk.Button(dialog, text="취소", command=dialog.destroy).grid(
        row=2, column=1, padx=10, pady=10
    )
    dialog.grab_set()


def toggle_wrap():
    text.config(wrap="word" if wrap_enabled.get() else "none")


# ---------- 보기 기능 ----------
def zoom_in():
    global zoom_percent
    zoom_percent = min(300, zoom_percent + 10)
    apply_font()


def zoom_out():
    global zoom_percent
    zoom_percent = max(50, zoom_percent - 10)
    apply_font()


def zoom_reset():
    global zoom_percent
    zoom_percent = 100
    apply_font()


def toggle_status():
    if status_visible.get():
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, before=editor_frame)
        update_status()
    else:
        status_bar.pack_forget()


def update_status(event=None):
    line, column = text.index(tk.INSERT).split(".")
    status_bar.config(text=f"줄 {line}, 열 {int(column) + 1}  |  {zoom_percent}%  |  UTF-8")


def on_modified(event=None):
    # 수정 여부는 저장 확인에 사용하므로 여기에서 False로 초기화하지 않습니다.
    update_status()


# ---------- 도움말 기능 ----------
def show_about():
    messagebox.showinfo(
        "프로그램정보", "수업용 메모장 1.0\nPython Tkinter 4단계 실습", parent=root
    )


# ---------- 창과 입력 영역 ----------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("850x550")
    current_file = None
    base_font_size = 12
    zoom_percent = 100
    wrap_enabled = tk.BooleanVar(value=True)
    status_visible = tk.BooleanVar(value=True)
    display_font = tkfont.nametofont("TkTextFont").copy()
    display_font.configure(size=base_font_size)

    # 아래쪽 상태 표시줄을 먼저 배치한 뒤 나머지 공간에 편집 영역을 채웁니다.
    status_bar = tk.Label(root, anchor="w", relief="sunken")
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    editor_frame = tk.Frame(root)
    editor_frame.pack(fill=tk.BOTH, expand=True)
    editor_frame.rowconfigure(0, weight=1)
    editor_frame.columnconfigure(0, weight=1)

    text = tk.Text(editor_frame, wrap="word", font=display_font)
    text.grid(row=0, column=0, sticky="nsew")
    y_scroll = ttk.Scrollbar(editor_frame, orient="vertical", command=text.yview)
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll = ttk.Scrollbar(editor_frame, orient="horizontal", command=text.xview)
    x_scroll.grid(row=1, column=0, sticky="ew")
    text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    text.edit_modified(False)

    # ---------- 메뉴 구성: 3단계의 구조를 유지하고 실제 함수로 연결 ----------
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="파일", menu=file_menu)
    file_menu.add_command(label="새파일", command=new_file)
    file_menu.add_command(label="열기", command=open_file)
    file_menu.add_command(label="저장", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="종료", command=exit_program)

    edit_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="편집", menu=edit_menu)
    edit_menu.add_command(label="잘라내기", command=cut_text)
    edit_menu.add_command(label="복사", command=copy_text)
    edit_menu.add_command(label="붙여넣기", command=paste_text)

    format_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="서식", menu=format_menu)
    format_menu.add_command(label="글꼴", command=change_font)
    format_menu.add_checkbutton(
        label="자동 줄바꿈", variable=wrap_enabled, command=toggle_wrap
    )

    view_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="보기", menu=view_menu)
    view_menu.add_command(label="확대", command=zoom_in)
    view_menu.add_command(label="축소", command=zoom_out)
    view_menu.add_command(label="기본 배율(100%)", command=zoom_reset)
    view_menu.add_separator()
    view_menu.add_checkbutton(
        label="상태 표시줄", variable=status_visible, command=toggle_status
    )

    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="도움말", menu=help_menu)
    help_menu.add_command(label="프로그램정보", command=show_about)

    text.bind("<KeyRelease>", update_status)
    text.bind("<ButtonRelease-1>", update_status)
    text.bind("<<Modified>>", on_modified)
    root.protocol("WM_DELETE_WINDOW", exit_program)
    update_title()
    update_status()
    text.focus_set()
    root.mainloop()
