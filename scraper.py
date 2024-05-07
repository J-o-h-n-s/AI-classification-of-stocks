import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv
import openai

news_urls = {
    "financial": "https://www.ft.com/us",
    "tech": "https://www.wired.com",
    "sports": "https://www.skysports.com/",
    "entertainment": "https://www.tmz.com",
}


def load_environment_variable(key):
    load_dotenv()
    return os.getenv(key)


def clean_headline(headline):
    """Clean headlines by removing newlines, punctuation, and extra spaces."""
    cleaned_headline = re.sub(r"[\r\n]+", " ", headline)
    cleaned_headline = re.sub(r"[!?]+", "", cleaned_headline)
    cleaned_headline = re.sub(r"[\.,]+", "", cleaned_headline)
    cleaned_headline = re.sub(r"\s+", " ", cleaned_headline)
    return cleaned_headline.strip()


def fetch_headlines(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    selector_map = {
        "www.ft.com": ".js-teaser-heading-link",
        "www.wired.com": ".summary-item__hed",
        "www.skysports.com": ".sdc-site-tile__headline-link",
        "www.tmz.com": ".article__header-title",
    }

    domain = url.split("/")[2]
    selector = selector_map.get(domain, "Unsupported URL")
    if selector == "Unsupported URL":
        print(f"Unsupported URL for domain: {domain}")
        return []

    headlines_elements = soup.select(selector)[:2]
    return [clean_headline(headline.text) for headline in headlines_elements]


def summarize_headlines(api_key, all_headlines):
    """Summarize headlines using OpenAI's GPT-3.5 Turbo."""
    prompt_text = (
        "Summarize the following news headlines into key insights:\n\n"
        + "\n".join(all_headlines)
    )

    messages = [{"role": "system", "content": prompt_text}]

    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content.strip()


def main():
    all_headlines = []
    api_key = load_environment_variable("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API Key not found. Please check your .env file.")

    for sector, url in news_urls.items():
        try:
            headlines = fetch_headlines(url)
            all_headlines.extend(headlines)
        except requests.HTTPError as e:
            print(f"Failed to fetch headlines from {sector}. Error: {e}")
        except Exception as e:
            print(
                f"An error occurred while fetching headlines from {sector}. Error: {e}"
            )

    summary = summarize_headlines(api_key, all_headlines)
    print(summary)


if __name__ == "__main__":
    main()
