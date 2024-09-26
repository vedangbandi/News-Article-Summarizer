import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import pipeline

def check_url_status(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        print(f"An error occurred while checking the URL status: {e}")
        return False

def fetch_article_selenium(url):
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    service = Service('C:/path/to/geckodriver.exe')  # Update this path
    driver = webdriver.Firefox(service=service, options=firefox_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "p"))
        )
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        article_text = ' '.join([para.text for para in paragraphs])
        return article_text
    except Exception as e:
        print(f"An error occurred while fetching the article: {e}")
        return None
    finally:
        driver.quit()

def summarize_article(article_text, max_chunk_size=1024):
    summarizer = pipeline("summarization")

    def chunk_text(text, max_chunk_size):
        words = text.split()
        return [ ' '.join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size) ]

    try:
        chunks = chunk_text(article_text, max_chunk_size)
        summaries = []
        for chunk in chunks:
            summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        return ' '.join(summaries)
    except Exception as e:
        print(f"An error occurred while summarizing the article: {e}")
        return None

def submit_url():
    url = url_entry.get()
    if not check_url_status(url):
        messagebox.showerror("Error", "The URL is not reachable. Please check the URL and try again.")
        return

    article_text = fetch_article_selenium(url)
    if article_text:
        summary = summarize_article(article_text)
        if summary:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, summary)
        else:
            messagebox.showerror("Error", "Failed to generate summary.")
    else:
        messagebox.showerror("Error", "Failed to retrieve the article. Please check the URL and try again.")

def clear_text():
    url_entry.delete(0, tk.END)
    output_text.delete(1.0, tk.END)

def take_screenshot():
    # Placeholder function for screenshot functionality
    messagebox.showinfo("Screenshot", "Screenshot functionality not implemented yet.")

def flag_article():
    # Placeholder function for flagging functionality
    messagebox.showinfo("Flag", "Flag functionality not implemented yet.")

# GUI setup
root = tk.Tk()
root.title("URL Based News Summarizer")

# Title
title_label = ttk.Label(root, text="News Summarizer", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=3, pady=10)

# Subtitle
subtitle_label = ttk.Label(root, text="Note: Shorter articles generate faster summaries.")
subtitle_label.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

# URL Entry
url_label = ttk.Label(root, text="URL")
url_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
url_entry = ttk.Entry(root, width=70)
url_entry.grid(row=2, column=1, padx=10, pady=5)

# Buttons for Screenshot, Clear, Submit, and Flag
screenshot_btn = ttk.Button(root, text="Screenshot", command=take_screenshot)
screenshot_btn.grid(row=2, column=2, padx=5, pady=5)

clear_btn = ttk.Button(root, text="Clear", command=clear_text)
clear_btn.grid(row=3, column=0, padx=5, pady=5)

submit_btn = ttk.Button(root, text="Submit", command=submit_url)
submit_btn.grid(row=3, column=1, padx=5, pady=5)

flag_btn = ttk.Button(root, text="Flag", command=flag_article)
flag_btn.grid(row=3, column=2, padx=5, pady=5)

# Output Textbox
output_label = ttk.Label(root, text="Output")
output_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
output_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

# Examples Section (can be further developed)
examples_label = ttk.Label(root, text="Examples")
examples_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
example_list = tk.Listbox(root, width=80, height=3)
example_list.insert(1, "https://www.technologyreview.com/2021/07/22/1029973/deepmind-alphafold-protein-folding-biology-disease-drugs-proteome/")
example_list.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

# Start the GUI
root.mainloop()
