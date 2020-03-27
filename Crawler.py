from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import pandas as pd

def search_link(kanji):
    return 'https://ja.dict.naver.com/#/search?query=' + kanji


def selenium_get_html(kanji):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(search_link(kanji))
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'word'))
            )
        finally:
            return driver.page_source


def crawl(kanji):
    html = selenium_get_html(kanji)
    soup = BeautifulSoup(html, 'html.parser')
    um = soup.select('#searchPage_entry > div > div:nth-child(1) > ul > li:nth-child(1) > div > span')
    hun = soup.select('#searchPage_entry > div > div:nth-child(1) > ul > li:nth-child(2) > div > span')
    mean = soup.select('#searchPage_entry > div > div:nth-child(1) > ul > li:nth-child(5) > div > span:nth-child(2)')
    if not mean:
        mean = soup.select('#searchPage_entry > div > div:nth-child(1) > ul > li:nth-child(4) > div > span:nth-child(2)')
    print(um, hun, mean)
    try:
        um = um[0].text
    except (IndexError, ValueError):
        um = ''

    try:
        hun = hun[0].text
    except (IndexError, ValueError):
        hun = ''

    try:
        mean = mean[0].text[1:-1]
    except (IndexError, ValueError):
        mean = ''

    kanji_data = {'um': um, 'hun': hun, 'mean': mean}
    print(kanji_data)
    return kanji_data


def read_csv(file):
    with open(file) as csv_file:
        csv_reader = csv.DictReader(csv_file)


if __name__ == '__main__':
    print('start running')
    df = pd.read_csv('Data/Heisigs RTK 6th Edition.csv')
    for i in range(0, len(df)):
        row = df.iloc[i]
        if 'um' in row and not pd.isnull(row['um']):
            continue
        kanji = row['kanji']
        kanji_data = crawl(kanji)
        df.at[i, 'um'] = kanji_data['um']
        df.at[i, 'hun'] = kanji_data['hun']
        df.at[i, 'mean'] = kanji_data['mean']
        print(df.iloc[i])
        df.to_csv('anki.csv', index=False, header=True, encoding='utf-8-sig')
