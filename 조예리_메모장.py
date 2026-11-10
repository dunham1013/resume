import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from pathlib import Path
import json
import os
import re

CONFIG_FILE="notepad_config.json"
DEFAULT_CONFIG={
    "width":800,
    "height":600,
    "x":100,
    "y":100,
    "zoom_percent":100,
    "font_size":11,
    "status_visible":True,
    "wrap_enabled":True,
    "dark_mode":False,
    "markdown_highlight":True,
    "line_numbers":True
}

def update_line_numbers(event=None):
    line_number_canvas.delete("all")
    if not line_numbers_visible.get():
        return
    end_index = text.index("@0,0")
    total_lines = int(text.index("end-1c").split(".")[0])
    current_line = 1
    while current_line <= total_lines:
        dline = text.dlineinfo(f"{current_line}.0")
        if dline is not None:
            y_coord = dline[1]
            if dark_mode.get():
                line_number_canvas.create_text(
                    35, y_coord, anchor="ne", text=str(current_line), fill="#858585", font=display_font
                )
            else:
                line_number_canvas.create_text(
                    35, y_coord, anchor="ne", text=str(current_line), fill="#6b6b6b", font=display_font
                )
        current_line += 1

def toggle_line_numbers():
    if line_numbers_visible.get():
        line_number_canvas.grid(row=0, column=0, sticky="ns")
    else:
        line_number_canvas.grid_remove()
    update_line_numbers()

def auto_save_handler():
    global auto_save_timer
    if current_file and text.edit_modified():
        try:
            Path(current_file).write_text(text.get("1.0", "end-1c"), encoding="utf-8")
            text.edit_modified(False)
            print("[알림] 백그라운드 자동 저장 완료")
        except Exception as e:
            print(f"[오류] 자동 저장 실패: {e}")
    auto_save_timer = root.after(30000, auto_save_handler)

def highlight_text(event=None):
    for tag in ["md_h1", "md_h2", "md_bold", "md_code"]:
        text.tag_remove(tag, "1.0", tk.END)
    if not markdown_highlight.get():
        return
    content = text.get("1.0", tk.END)
    if dark_mode.get():
        h1_color = "#569cd6"
        h2_color = "#4ec9b0"
        bold_color = "#ce9178"
        code_color = "#dcdcaa"
    else:
        h1_color = "#0000ff"
        h2_color = "#008000"
        bold_color = "#a31515"
        code_color = "#af00db"
    text.tag_config("md_h1", foreground=h1_color, font=(display_font.actual("family"), int(display_font.actual("size") * 1.3), "bold"))
    text.tag_config("md_h2", foreground=h2_color, font=(display_font.actual("family"), int(display_font.actual("size") * 1.15), "bold"))
    text.tag_config("md_bold", foreground=bold_color, font=(display_font.actual("family"), display_font.actual("size"), "bold"))
    text.tag_config("md_code", foreground=code_color)
    for match in re.finditer(r"^# .+$", content, re.MULTILINE):
        start_idx = f"1.0 + {match.start()} chars"
        end_idx = f"1.0 + {match.end()} chars"
        text.tag_add("md_h1", start_idx, end_idx)
    for match in re.finditer(r"^## .+$", content, re.MULTILINE):
        start_idx = f"1.0 + {match.start()} chars"
        end_idx = f"1.0 + {match.end()} chars"
        text.tag_add("md_h2", start_idx, end_idx)
    for match in re.finditer(r"\*\*(.+?)\*\*", content):
        start_idx = f"1.0 + {match.start()} chars"
        end_idx = f"1.0 + {match.end()} chars"
        text.tag_add("md_bold", start_idx, end_idx)
    for match in re.finditer(r"`(.+?)`", content):
        start_idx = f"1.0 + {match.start()} chars"
        end_idx = f"1.0 + {match.end()} chars"
        text.tag_add("md_code", start_idx, end_idx)

def change_text_color(color_name):
    try:
        text.tag_add(f"color_{color_name}", "sel.first", "sel.last")
        if dark_mode.get() and color_name in ["black", "#000000"]:
            text.tag_config(f"color_{color_name}", foreground="#ffffff")
        else:
            text.tag_config(f"color_{color_name}", foreground=color_name)
    except tk.TclError:
        pass

def toggle_markdown_highlight():
    highlight_text()

def toggle_dark_mode():
    if dark_mode.get():
        text.config(
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            selectbackground="#264f78",
            relief="flat",
            borderwidth=0
        )
        status_bar.config(bg="#2d2d2d", fg="#a0a0a0", relief="flat")
        editor_frame.config(bg="#1e1e1e")
        root.config(bg="#1e1e1e")
        for tag in text.tag_names():
            if tag.startswith("color_"):
                curr_fg=text.tag_cget(tag, "foreground")
                if curr_fg in ["black", "#000000", "#111111", "#222222"]:
                    text.tag_config(tag, foreground="#ffffff")
    else:
        text.config(
            bg="white",
            fg="black",
            insertbackground="black",
            selectbackground="#0078d7",
            relief="sunken",
            borderwidth=1
        )
        status_bar.config(bg="#f0f0f0", fg="black", relief="sunken")
        editor_frame.config(bg="#f0f0f0")
        root.config(bg="#f0f0f0")
        for tag in text.tag_names():
            if tag.startswith("color_"):
                orig_color=tag.replace("color_", "")
                text.tag_config(tag, foreground=orig_color)
    highlight_text()
    update_line_numbers()

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config=json.load(f)
                for key, val in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key]=val
                return config
        except (json.JSONDecodeError, PermissionError) as e:
            print(f"[경고] 설정 파일 읽기 오류:{e}. 기본값으로 대체합니다.")
    return DEFAULT_CONFIG.copy()

def save_config():
    try:
        config={
            "width":root.winfo_width(),
            "height":root.winfo_height(),
            "x":root.winfo_x(),
            "y":root.winfo_y(),
            "zoom_percent":zoom_percent,
            "font_size":base_font_size,
            "status_visible":status_visible.get(),
            "wrap_enabled":wrap_enabled.get(),
            "dark_mode":dark_mode.get(),
            "markdown_highlight":markdown_highlight.get(),
            "line_numbers":line_numbers_visible.get()
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[오류] 설정 저장 실패:{e}")

def update_title():
    name=Path(current_file).name if current_file else "제목 없음"
    root.title(f"{name}")

def open_file():
    global current_file
    if not confirm_save():
        return
    path=filedialog.askopenfilename(
        parent=root, title="열기", filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
    )
    if not path:
        return
    try:
        content=Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        messagebox.showerror(
            "열기 오류", f"utf-8 텍스트 파일을 선택해 주세요.\n{error}", parent=root
        )
        return
    text.delete("1.0", tk.END)
    text.insert("1.0", content)
    text.edit_modified(False)
    current_file=path
    update_title()
    update_status()
    text.focus_set()
    highlight_text()
    update_line_numbers()

def save_file():
    global current_file
    path=current_file or filedialog.asksaveasfilename(parent=root, title="저장", defaultextension=".txt", filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
    if not path:
        return False
    try:
        Path(path).write_text(text.get("1.0", "end-1c"), encoding="utf-8")
    except (OSError, UnicodeError) as error:
        messagebox.showerror("저장 오류", str(error), parent=root)
        return False
    current_file=path
    text.edit_modified(False)
    update_title()
    return True

def confirm_save():
    if not text.edit_modified():
        return True
    answer=messagebox.askyesnocancel(
        "저장 확인", "변경한 내용을 저장하시겠습니까?", parent=root
    )
    if answer is None:
        return False
    return save_file() if answer else True

def new_file():
    global current_file
    if not confirm_save():
        return
    text.delete("1.0", tk.END)
    text.edit_modified(False)
    current_file=None
    update_title()
    update_status()
    text.focus_set()
    update_line_numbers()

def exit_program():
    if confirm_save():
        save_config()
        root.destroy()

def cut_file():
    text.focus_set()
    text.event_generate("<<Cut>>")

def copy_file():
    text.focus_set()
    text.event_generate("<<Copy>>")

def paste_file():
    text.focus_set()
    text.event_generate("<<Paste>>")

def apply_font():
    actual_size=max(1, round(base_font_size*zoom_percent/100))
    display_font.configure(size=actual_size)
    update_status()
    update_line_numbers()

def change_font():
    dialog=tk.Toplevel(root)
    dialog.title("글꼴")
    dialog.resizable(False, False)
    dialog.transient(root)
    ttk.Label(dialog, text="글꼴").grid(row=0, column=0, padx=10, pady=10)
    family_box=ttk.Combobox(
        dialog, values=sorted(set(tkfont.families(root))), state="readonly", width=28
    )
    family_box.set(display_font.actual("family"))
    family_box.grid(row=0, column=1, padx=10, pady=10)
    ttk.Label(dialog, text="기본 크기(8-72)").grid(row=1, column=0, padx=10, pady=10)
    size_var=tk.StringVar(value=str(base_font_size))
    ttk.Spinbox(dialog, from_=8, to=72, textvariable=size_var, width=8).grid(
        row=1, column=1, padx=10, pady=10, sticky="w"
    )
    def apply_selection():
        global base_font_size
        try:
            size=int(size_var.get())
            if not 8<=size<=72:
                raise ValueError
        except ValueError:
            messagebox.showerror("크기 오류", "8-72의 정수를 입력해 주세요.", parent=dialog)
            return
        base_font_size=size
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

def zoom_in():
    global zoom_percent
    zoom_percent=min(300, zoom_percent+10)
    apply_font()

def zoom_out():
    global zoom_percent
    zoom_percent=max(50, zoom_percent-10)
    apply_font()

def zoom_reset():
    global zoom_percent
    zoom_percent=100
    apply_font()

def toggle_status():
    if status_visible.get():
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, before=editor_frame)
        update_status()
    else:
        status_bar.pack_forget()

def update_status(event=None):
    line, column=text.index(tk.INSERT).split(".")
    status_bar.config(text=f"줄 {line}, 열{int(column)+1}|{zoom_percent}%|utf-8")

def on_modified(event=None):
    update_status()
    highlight_text()
    text.edit_modified(False)
    
def about_file():
    messagebox.showinfo("프로그램 정보", "프로그램 정보 메뉴 선택", parent=root)

if __name__=="__main__":
    root=tk.Tk()
    saved_config=load_config()
    current_file=None
    base_font_size=saved_config["font_size"]
    zoom_percent=saved_config["zoom_percent"]
    wrap_enabled=tk.BooleanVar(value=saved_config["wrap_enabled"])
    status_visible=tk.BooleanVar(value=saved_config["status_visible"])
    dark_mode=tk.BooleanVar(value=saved_config["dark_mode"])
    markdown_highlight=tk.BooleanVar(value=saved_config["markdown_highlight"])
    line_numbers_visible=tk.BooleanVar(value=saved_config["line_numbers"])
    root.geometry(f"{saved_config['width']}x{saved_config['height']}+{saved_config['x']}+{saved_config['y']}")
    # root.geometry("800x500")
    current_file=None
    # base_font_size=12
    # zoom_percent=100
    # wrap_enabled=tk.BooleanVar(value=True)
    # status_visible=tk.BooleanVar(value=True)
    display_font=tkfont.nametofont("TkTextFont").copy()
    display_font.configure(size=base_font_size)
    status_bar=tk.Label(root, anchor="w", relief="sunken")
    if saved_config["status_visible"]:
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    editor_frame=tk.Frame(root)
    editor_frame.pack(fill=tk.BOTH, expand=True)
    editor_frame.rowconfigure(0, weight=1)
    editor_frame.columnconfigure(1, weight=1)
    line_number_canvas=tk.Canvas(editor_frame, width=45, bg="#f0f0f0", highlightthickness=1)
    if saved_config["line_numbers"]:
        line_number_canvas.grid(row=0, column=0, sticky="ns")
    initial_wrap="word" if saved_config["wrap_enabled"] else "none"
    text=tk.Text(editor_frame, wrap=initial_wrap, font=display_font)
    # text=tk.Text(editor_frame, wrap="word", font=display_font)
    text.grid(row=0, column=1, sticky="nsew")
    y_scroll=ttk.Scrollbar(editor_frame, orient="vertical", command=text.yview)
    y_scroll.grid(row=0, column=2, sticky="ns")
    x_scroll=ttk.Scrollbar(editor_frame, orient="horizontal", command=text.xview)
    x_scroll.grid(row=1, column=1, sticky="ew")
    text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    text.edit_modified(False)
    toggle_dark_mode()

# 메뉴 막대 창 연결
    menu_bar=tk.Menu(root)
    root.config(menu=menu_bar)

# 파일
    file_menu=tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="파일", menu=file_menu)
    file_menu.add_command(label="새파일", command=new_file)
    file_menu.add_command(label="열기", command=open_file)
    file_menu.add_command(label="저장", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="종료", command=exit_program)

# 편집
    edit_menu=tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="편집", menu=edit_menu)
    edit_menu.add_command(label="잘라내기", command=cut_file)
    edit_menu.add_command(label="복사하기", command=copy_file)
    edit_menu.add_command(label="붙여넣기", command=paste_file)

# 서식
    format_menu=tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="서식", menu=format_menu)
    format_menu.add_command(label="글꼴", command=change_font)
    format_menu.add_checkbutton(
        label="자동 줄바꿈", variable=wrap_enabled, command=toggle_wrap
    )

#보기
    view_menu=tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="보기", menu=view_menu)
    view_menu.add_command(label="확대", command=zoom_in)
    view_menu.add_command(label="축소", command=zoom_out)
    view_menu.add_command(label="기본 배율(100%)", command=zoom_reset)
    view_menu.add_separator()
    view_menu.add_checkbutton(
        label="상태 표시줄", variable=status_visible, command=toggle_status
    )
    view_menu.add_checkbutton(
        label="다크 모드", variable=dark_mode, command=toggle_dark_mode
    )
    view_menu.add_checkbutton(
        label="마크다운 하이라이트", variable=markdown_highlight, command=toggle_markdown_highlight
    )
    view_menu.add_checkbutton(
        label="줄 번호", variable=line_numbers_visible, command=toggle_line_numbers
    )

# 도움말
    help_menu=tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="도움말", menu=help_menu)
    help_menu.add_command(label="프로그램 정보", command=about_file)

    text.bind("<KeyRelease>", update_line_numbers)
    text.bind("<ButtonRelease-1>", update_line_numbers)
    text.bind("<MouseWheel>", update_line_numbers)
    text.bind("<<Modified>>", on_modified)
    root.protocol("WM_DELETE_WINDOW", exit_program)
    auto_save_timer=root.after(30000, auto_save_handler)
    update_title()
    update_status()
    update_line_numbers()
    text.focus_set()
    root.mainloop()