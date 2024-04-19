import tkinter as tk
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup
import webbrowser
import os
import sys
import ctypes

def crawl_news(search_query, num_results):
    # 검색어를 이용하여 네이버 뉴스에서 소식 크롤링
    news_list = []
    page = 1
    while len(news_list) < num_results:
        url = f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_query}&start={page}"
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        titles = soup.select(".news_tit")

        for title in titles:
            news_title = title.text
            news_link = title['href']
            news_list.append((news_title, news_link))
            if len(news_list) >= num_results:
                break

        page += 10

    return news_list[:num_results]

def search_button_clicked():

    if checkVali():
        return

    search_query = search_entry.get()
    num_results = int(result_count_entry.get())  # 입력 칸에서 개수를 가져옴

    # 소식 크롤링 실행
    news = crawl_news(search_query, num_results)

    # 결과를 GUI 창에 표시
    result_text.configure(state="normal")  # 읽기 전용 해제
    result_text.delete("1.0", tk.END)  # 기존 텍스트 삭제

    for i, (news_title, news_link) in enumerate(news, start=1):
        result_text.insert(tk.END, f"ㆍ ")
        result_text.insert(tk.END, f"{news_title}", f"link_{i}")
        result_text.insert(tk.END, f"\n\n")
        result_text.tag_config(f"link_{i}", font=("Arial", 10))  # 폰트 설정
        result_text.tag_bind(f"link_{i}", "<Button-1>", lambda event, link=news_link: open_link(link))
        result_text.tag_bind(f"link_{i}", "<Enter>", lambda event, tag=f"link_{i}": set_hover_style(tag))
        result_text.tag_bind(f"link_{i}", "<Leave>", lambda event, tag=f"link_{i}": reset_hover_style(tag))

    result_text.configure(state="disabled")  # 읽기 전용 설정

def open_link(link):
    webbrowser.open_new_tab(link)

def clear_search_entry(event):
    search_entry.delete(0, tk.END)

def enter_key_pressed(event):
    search_button_clicked()

def checkVali():
    entryChk = search_entry.get()
    countChk = result_count_entry.get()

    if len(entryChk.strip()) == 0 or entryChk is None or entryChk.strip() == "검색어를 입력하세요":
        ctypes.windll.user32.MessageBoxW(0, "검색어를 입력해주세요.", "알림", 16)
        return True
    
    if len(countChk.strip()) == 0 or countChk is None:
        ctypes.windll.user32.MessageBoxW(0, "개수를 입력해주세요.", "알림", 16)
        return True
    
    if int(countChk) > 200:
        ctypes.windll.user32.MessageBoxW(0, "검색할 수 있는 최대 수를 초과했습니다.", "알림", 16)
        return True
    
    return False

def set_hover_style(tag):
    result_text.tag_config(tag, foreground="blue", font=("Arial", 10, "bold"))
    result_text.config(cursor="hand2")
    result_text.tag_bind(tag, "<Enter>", lambda event, tag=tag: set_hover_style(tag))
    result_text.tag_bind(tag, "<Leave>", lambda event, tag=tag: reset_hover_style(tag))

def reset_hover_style(tag):
    result_text.tag_config(tag, foreground="black", font=("Arial", 10))
    result_text.config(cursor="arrow")
    result_text.tag_bind(tag, "<Enter>", lambda event, tag=tag: set_hover_style(tag))
    result_text.tag_bind(tag, "<Leave>", lambda event, tag=tag: reset_hover_style(tag))

def validate_input(text):
    if text.isdigit() or text == "":
        return True
    else:
        return False

# GUI 창 생성
root = tk.Tk()
root.title("뉴스 검색")
root.geometry("600x500")  # GUI 창 크기 설정

# 아이콘 이미지 설정
# 실행 파일의 경로와 아이콘 파일의 경로를 결합
base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
icon_path = os.path.join(base_path, "icon.ico")
root.iconbitmap(icon_path)

# 검색어 입력 필드 생성
search_frame = tk.Frame(root)
search_frame.pack(anchor=tk.W, padx=10, pady=(10, 0))

search_label = tk.Label(search_frame, text="검색어:", font=("Arial", 10))
search_label.pack(side=tk.LEFT)

search_entry = tk.Entry(search_frame, width=72, font=("Arial", 10))  # font 크기 조정, width 조정
search_entry.pack(side=tk.LEFT, expand=True, padx=(5, 0))
search_entry.insert(0, "검색어를 입력하세요")  # 검색어 입력 창의 placeholder 설정
search_entry.bind("<FocusIn>", clear_search_entry)  # 포커스를 받으면 내용 초기화
search_entry.bind("<Return>", enter_key_pressed)  # 엔터 키를 누르면 검색 버튼 동작

# 검색 결과 개수 입력 필드 생성
result_count_frame = tk.Frame(root)
result_count_frame.pack(anchor=tk.W, padx=22, pady=(0, 10))

result_count_label = tk.Label(result_count_frame, text="개수:", font=("Arial", 10))
result_count_label.pack(side=tk.LEFT)

validate_func = root.register(validate_input)

result_count_entry = tk.Entry(result_count_frame, width=5, font=("Arial", 10), validate="key", validatecommand=(validate_func, '%P'))  # font 크기 조정, width 조정
result_count_entry.pack(side=tk.LEFT, padx=6)
result_count_entry.insert(0, "10")  # 기본적으로 10개의 결과를 가져옴
result_count_entry.bind("<Return>", enter_key_pressed)  # 엔터 키를 누르면 검색 버튼 동작

# 검색 버튼 생성
search_button = tk.Button(root, text="검색", command=search_button_clicked, font=("Arial", 10))
search_button.pack(padx=10, pady=(0, 10))

# 결과 텍스트 상자 생성
result_label = tk.Label(root, text="최근 소식:", font=("Arial", 10))
result_label.pack(anchor=tk.W, padx=10, pady=(10, 0))

result_text = scrolledtext.ScrolledText(root, width=60, height=25, font=("Arial", 10))  # font 크기 조정, height 조정
result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
result_text.configure(state="disabled")  # 읽기 전용 설정

# GUI 창 실행
root.mainloop()