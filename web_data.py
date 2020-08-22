from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import csv
import re
import plotly.figure_factory as ff
import numpy as np
import geopandas
import shapefile
import shapely
import plotly.express as px
import us

# TODO: gather the last ten titles
# Only use this to reload titles.csv
def titles_import():
    titles = []
    i = 19
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

def read_populations_from_csv():
    extracted_pops = {}
    with open('populations.csv') as csvfile:
        titlereader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in titlereader:
            state_abbr = us.states.lookup(row[0]).abbr
            state_pop = int(row[1])
            extracted_pops[state_abbr] = state_pop
        return extracted_pops

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
        if (us.states.lookup(state) != None):
            temp = us.states.lookup(state).abbr
            states.append(temp)
    return states

def ranking(list):
    loc_count = {}
    for loc in list:
        if loc in loc_count:
            loc_count[loc] += 1
        else:
            loc_count[loc] = 1
    return loc_count

def divide_by_pop(list):
    pops = read_populations_from_csv()
    for state in list.keys():
        # get the number of stories per 1mil people
        div = pops[state]/1000000
        list[state] = list[state]/div
    return list

data = divide_by_pop(ranking(states(locations(read_titles_from_csv()))))
locs = list(data.keys())
ranks = list(data.values())
print(data)
fig = px.choropleth(locations=locs, locationmode="USA-states", color=ranks, scope="usa", color_continuous_scale=px.colors.sequential.Blues)
fig.show()