import tkinter as tk
from tkinter import messagebox

def new_file():
    messagebox.showinfo("새파일", "새파일 메뉴 선택", parent=root)

def open_file():
    messagebox.showinfo("열기", "열기 메뉴 선택", parent=root)

def save_file():
    messagebox.showinfo("저장", "저장 메뉴 선택", parent=root)

def cut_file():
    # 핵심 코드
    # content=text.get("1.0", "end-1c")
    # Path(path).write_text(content, encoding="utf-8")

def copy_file():
    messagebox.showinfo("복사하기", "복사하기 메뉴 선택", parent=root)

def paste_file():
    messagebox.showinfo("붙여넣기", "붙여넣기 메뉴 선택", parent=root)

def about_file():
    messagebox.showinfo("프로그램 정보", "프로그램 정보 메뉴 선택", parent=root)

root=tk.Tk()
root.title("첫 메모장")
root.geometry("800x500")

text=tk.Text(root, wrap="word")
text.pack(fill=tk.BOTH, expand=True)
text.focus_set()

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
file_menu.add_command(label="종료", command=root.destroy)

# 편집
edit_menu=tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="편집", menu=edit_menu)
edit_menu.add_command(label="잘라내기", command=cut_file)
edit_menu.add_command(label="복사하기", command=copy_file)
edit_menu.add_command(label="붙여넣기", command=paste_file)

# 도움말
help_menu=tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="도움말", menu=help_menu)
help_menu.add_command(label="프로그램 정보", command=about_file)

root.mainloop()