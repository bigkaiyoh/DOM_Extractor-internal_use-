import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Selenium Setup
def init_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Extract Content Dynamically with Selenium
def fetch_dynamic_content(url):
    driver = init_selenium()
    driver.get(url)
    page_source = driver.page_source
    driver.quit()
    return page_source

# Extract Metadata, Lists, Tables, and Contact Info
def fetch_url_content(urls, dynamic=False):
    results = []
    for url in urls:
        try:
            # Get HTML content (use Selenium if dynamic=True)
            if dynamic:
                html_content = fetch_dynamic_content(url)
            else:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                html_content = response.content

            soup = BeautifulSoup(html_content, 'html.parser')

            # Metadata
            title = soup.title.string if soup.title else "No title"
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else "No description"
            h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
            h2_tags = [h2.text.strip() for h2 in soup.find_all('h2')]

            # Lists
            lists = [[li.text.strip() for li in ul.find_all('li')] for ul in soup.find_all('ul')]

            # Tables
            try:
                tables = pd.read_html(html_content)
                extracted_tables = [table.to_dict(orient='records') for table in tables]
            except ValueError:
                extracted_tables = []

            # Links
            links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]

            # Contact Information
            raw_text = soup.get_text()
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
            phones = re.findall(r'\+?\d{1,4}[\s-]?\(?\d+\)?[\s-]?\d+[\s-]?\d+', raw_text)

            # Append Results
            results.append({
                'url': url,
                'status': 'Success',
                'title': title,
                'description': description,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'lists': lists,
                'tables': extracted_tables,
                'links': links,
                'contact_info': {
                    'emails': emails,
                    'phones': phones
                }
            })
        except Exception as e:
            results.append({
                'url': url,
                'status': 'Failed',
                'error': str(e)
            })
    return results

# Streamlit App
def main():
    st.title("Dynamic Web Scraper")
    st.write("URLを入力して、ウェブページから構造化データと非構造化データを抽出します。")

    # Input Section
    urls_input = st.text_area("URLを入力してください（1行につき1つのURL）:", height=150)
    st.write("**動的コンテンツ読み込みについて:** 動的コンテンツ読み込みを有効にすると、JavaScriptで生成されたページ内容も取得できます。例えば、商品のリストや動的に生成される情報が必要な場合にオンにしてください。ただし、処理速度が遅くなる可能性があります。")
    dynamic_loading = st.checkbox("動的コンテンツ読み込みを有効にする (Selenium)", value=False)
    output_format = st.radio("出力形式を選択してください:", options=["JSON", "プレーンテキスト"], index=0)
    fetch_button = st.button("データを取得・抽出")

    if fetch_button:
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        if urls:
            results = fetch_url_content(urls, dynamic=dynamic_loading)

            # Format Results
            if output_format == "JSON":
                formatted_results = json.dumps(results, indent=4, ensure_ascii=False)
            else:
                formatted_results = "\n\n".join([f"URL: {res['url']}\nステータス: {res['status']}\nタイトル: {res.get('title', 'No title')}\n説明: {res.get('description', 'No description')}\n"
                                                 for res in results])

            # Display Results
            st.subheader("抽出結果")
            st.text_area("出力:", formatted_results, height=400)

            # Optional Copy Button
            st.write("上記の結果をコピーしてワークフローで使用してください。")
        else:
            st.error("少なくとも1つの有効なURLを入力してください。")

if __name__ == "__main__":
    main()
