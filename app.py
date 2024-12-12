import streamlit as st
import requests
from bs4 import BeautifulSoup
import pyperclip

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

            results.append({
                'url': url,
                'status': 'Success',
                'title': title,
                'description': description,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'paragraphs': paragraphs
            })
        except requests.exceptions.RequestException as e:
            results.append({
                'url': url,
                'status': 'Failed',
                'error': str(e)
            })
    return results

# Function to format the output for ChatGPT
def format_for_chatgpt(results):
    output = "# Webpage Scraping Results\n\n"
    for result in results:
        if result['status'] == 'Success':
            output += f"## URL: {result['url']}\n"
            output += f"### Status: Success\n"
            output += f"### Title: {result['title']}\n"
            output += f"### Description: {result['description']}\n"
            output += f"### H1 Tags: {', '.join(result['h1_tags'])}\n"
            output += f"### H2 Tags: {', '.join(result['h2_tags'])}\n"
            output += "### Key Paragraphs:\n"
            for paragraph in result['paragraphs']:
                output += f"- {paragraph}\n"
        else:
            output += f"## URL: {result['url']}\n"
            output += f"### Status: Failed\n"
            output += f"Error: {result['error']}\n"
        output += "\n"
    return output

# Streamlit App
def main():
    st.title("Nuginy Internal Webpage DOM Scraper")
    st.write("Input URLs to fetch their DOM and prepare it for ChatGPT.")

    # Input section
    if "formatted_output" not in st.session_state:
        st.session_state["formatted_output"] = ""

    urls_input = st.text_area("Enter URLs (one per line):")
    fetch_button = st.button("Fetch and Format")

    if fetch_button:
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        if urls:
            results = fetch_url_content(urls)
            st.session_state["formatted_output"] = format_for_chatgpt(results)

            # Display output
            st.subheader("Formatted Output")
            st.text_area("Copy this text to paste into ChatGPT:", st.session_state["formatted_output"], height=300)
        else:
            st.error("Please enter at least one valid URL.")

    # Copy-to-clipboard button
    if st.session_state["formatted_output"]:
        copy_button = st.button("Copy to Clipboard")
        if copy_button:
            try:
                pyperclip.copy(st.session_state["formatted_output"])
                st.success("Output copied to clipboard!")
            except Exception as e:
                st.error(f"Failed to copy to clipboard: {e}")

if __name__ == "__main__":
    main()
