from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# TODO: gather the last ten titles
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

data_import()