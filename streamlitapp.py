import streamlit as st
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import pipeline

# Function to check URL status
def check_url_status(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        st.error(f"An error occurred while checking the URL status: {e}")
        return False

# Function to fetch article using Selenium
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
        st.error(f"An error occurred while fetching the article: {e}")
        return None
    finally:
        driver.quit()

# Function to summarize the article
def summarize_article(article_text, max_chunk_size=1024):
    summarizer = pipeline("summarization")

    def chunk_text(text, max_chunk_size):
        words = text.split()
        return [' '.join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]

    try:
        chunks = chunk_text(article_text, max_chunk_size)
        summaries = []
        for chunk in chunks:
            summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        return ' '.join(summaries)
    except Exception as e:
        st.error(f"An error occurred while summarizing the article: {e}")
        return None

# Streamlit Interface
st.title("URL-Based News Summarizer")

st.write("Note: Shorter articles generate faster summaries.")

# Input for URL
url = st.text_input("Enter the URL of the article")

# Button for submitting the URL
if st.button("Summarize Article"):
    if check_url_status(url):
        with st.spinner("Fetching and summarizing article..."):
            article_text = fetch_article_selenium(url)
            if article_text:
                summary = summarize_article(article_text)
                if summary:
                    st.subheader("Summary")
                    st.write(summary)
                else:
                    st.error("Failed to generate summary.")
            else:
                st.error("Failed to retrieve the article. Please check the URL and try again.")
    else:
        st.error("The URL is not reachable. Please check the URL and try again.")

# Button to clear text input (Streamlit automatically clears text on re-run)
if st.button("Clear Input"):
    st.experimental_rerun()

# Example section (can be further developed)
st.write("Examples:")
st.write("[Example 1](https://www.technologyreview.com/2021/07/22/1029973/deepmind-alphafold-protein-folding-biology-disease-drugs-proteome/)")
