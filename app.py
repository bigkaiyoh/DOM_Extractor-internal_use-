import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# Function to fetch and process the DOM from a URL
def fetch_url_content(urls):
    results = []
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract key parts of the page
            title = soup.title.string if soup.title else "No title"
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else "No description"

            h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
            h2_tags = [h2.text.strip() for h2 in soup.find_all('h2')]
            paragraphs = [p.text.strip() for p in soup.find_all('p')]
            links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]

            results.append({
                'url': url,
                'status': 'Success',
                'title': title,
                'description': description,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'paragraphs': paragraphs,
                'links': links
            })
        except requests.exceptions.RequestException as e:
            results.append({
                'url': url,
                'status': 'Failed',
                'error': str(e)
            })
    return results

# Function to format the output as JSON for ChatGPT
def format_for_chatgpt(results):
    return json.dumps(results, indent=4, ensure_ascii=False)

# Streamlit App
def main():
    st.title("Nuginy Internal Webpage DOM Scraper")
    st.write("URLを入力して、DOMを取得し、ChatGPTで利用できるJSON形式にフォーマットします。")

    # Input section
    if "formatted_output" not in st.session_state:
        st.session_state["formatted_output"] = ""

    urls_input = st.text_area("URLを入力してください（1行につき1つのURLを入力）:")
    fetch_button = st.button("取得してフォーマット")

    if fetch_button:
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        if urls:
            results = fetch_url_content(urls)
            st.session_state["formatted_output"] = format_for_chatgpt(results)

            # Display output
            st.subheader("フォーマット済みのJSON出力")
            st.text_area("このJSONをコピーしてChatGPTに貼り付けてください:", st.session_state["formatted_output"], height=500)
        else:
            st.error("少なくとも1つの有効なURLを入力してください。")

if __name__ == "__main__":
    main()
