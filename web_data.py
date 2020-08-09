from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import csv
import re
import plotly.figure_factory as ff
import numpy as np

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

def states(list):
    states = []
    for town_and_state in list:
        # anything longer is the UK or some other place
        if len(town_and_state.split(",")) == 2:
            state = (town_and_state.split(","))[1].strip()
            states.append(state)
    return states

def ranking(list):
    loc_count = {}
    for loc in list:
        if loc in loc_count:
            loc_count[loc] += 1
        else:
            loc_count[loc] = 1
    return loc_count

df_sample = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/laucnty16.csv')
df_sample['State FIPS Code'] = df_sample['State FIPS Code'].apply(lambda x: str(x).zfill(2))
df_sample['County FIPS Code'] = df_sample['County FIPS Code'].apply(lambda x: str(x).zfill(3))
df_sample['FIPS'] = df_sample['State FIPS Code'] + df_sample['County FIPS Code']

colorscale = ["#f7fbff","#ebf3fb","#deebf7","#d2e3f3","#c6dbef","#b3d2e9","#9ecae1",
              "#85bcdb","#6baed6","#57a0ce","#4292c6","#3082be","#2171b5","#1361a9",
              "#08519c","#0b4083","#08306b"]
endpts = list(np.linspace(1, 12, len(colorscale) - 1))
fips = df_sample['FIPS'].tolist()
values = df_sample['Unemployment Rate (%)'].tolist()

fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='USA by Unemployment %',
    legend_title='% unemployed'
)

fig.layout.template = None
fig.show()
# ranking(states(locations(read_titles_from_csv())))