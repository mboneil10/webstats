from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import csv
import re

# TODO: gather the last ten titles
# Only use this to reload titles.csv
def data_import():
    titles = []
    i = 18
    driver = webdriver.Chrome(ChromeDriverManager().install())
    page = "https://podcasts.apple.com/us/podcast/small-town-murder/id1194755213"
    driver.get(page)
    while i > 0:
        # Wait for the next "Load more episodes" button to appear
        # Also don't want to get kicked off the site for traffic issues...
        time.sleep(5)
        # There are three buttons found with the following css selector.
        # Click the one in the middle, because that is the "Load more episodes" button
        (driver.find_elements_by_css_selector('button.link'))[1].click()
        i = i - 1
    content = driver.page_source
    data = BeautifulSoup(content, features="html.parser")
    for episode in data.findAll('div', attrs={'class': 'tracks__track__content'}):
        title = episode.find('a', attrs={'class': 'tracks__track__link--block'}).text.strip()
        titles.append(title)
    driver.close()
    df = pd.DataFrame({'Titles': titles})
    return df.to_csv('titles.csv', index=False, encoding='utf-8')

def read_titles_from_csv():
    extracted_titles = []
    with open('titles.csv') as csvfile:
        titlereader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in titlereader:
            extracted_titles.append(' '.join(row))
        return extracted_titles

def locations(list):
    locations = []
    index = 0
    for title in list:
        if re.search(r'- Part', title):
            index_of_town = re.search(r'- Part', title).start(0)
            title = title[:index_of_town]
        split_title = re.search(r'(?<=in)\b', title)
        if (split_title != None):
            index_of_town = split_title.start(0)
            location = title[index_of_town:].strip().replace('"', '')
            locations.append(location)
    return locations

print(locations(read_titles_from_csv()))