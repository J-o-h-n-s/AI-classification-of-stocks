import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import openai
from dotenv import load_dotenv
import glob


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def load_environment():
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")


def fetch_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "constituents"})
    return (
        [row.find("td").text.strip() for row in table.find_all("tr")[1:]]
        if table
        else []
    )


def classify_sectors_with_openai(api_key, tickers):
    client = openai.OpenAI(api_key=api_key)
    sectors = []
    for ticker in tickers:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are going to classify tickers in the S&P500 into sectors. Respond only with the sector.",
                },
                {"role": "user", "content": "AAPL"},
            ],
            temperature=0,
            max_tokens=20,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        sector = response.choices[0].message.content.strip()
        sectors.append(sector)
        print(f"{ticker}: {sector}")
    return sectors


def save_data(tickers, sectors, filename):
    data = pd.DataFrame({"Ticker": tickers, "Sector": sectors})
    data.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


def is_update_needed():
    current_date = datetime.now()
    files = glob.glob("./*_sp500_tickers_sectors.csv")
    if files:
        latest_file = max(files, key=os.path.getctime)
        try:
            date_str = os.path.basename(latest_file).split("_")[0]
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            return relativedelta(current_date, file_date).months > 3
        except (ValueError, IndexError):
            print(
                f"Invalid date format in file name {latest_file}, assuming update is needed."
            )
            return True
    return True


def get_sectors_or_update_sectors():
    if is_update_needed():
        api_key = load_environment()
        if not api_key:
            raise ValueError("API Key is missing. Please check your .env file.")
        sp500_tickers = fetch_sp500_tickers()
        sectors = classify_sectors_with_openai(api_key, sp500_tickers)
        filename = f"{datetime.now().strftime('%Y-%m-%d')}_sp500_tickers_sectors.csv"
        save_data(sp500_tickers, sectors, filename)
        return filename
    else:
        files = glob.glob("./*_sp500_tickers_sectors.csv")
        latest_file = max(files, key=os.path.getctime)
        return latest_file


def main():
    clear()
    if is_update_needed():
        get_sectors_or_update_sectors()
    else:
        print("File not older than 3 months. Skipping update")


if __name__ == "__main__":
    main()
