from os import listdir
from os.path import isfile, join
import json
from selenium import webdriver

data_folder = 'data'
onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
print(onlyfiles)

option = webdriver.ChromeOptions()
option.add_argument("--incognito")
browser = webdriver.Chrome(executable_path='chromedriver', chrome_options=option)

for file in sorted(onlyfiles):
    item_id = file.split(".")[0]
    if item_id == 'comments':
        continue
    with open('data/' + file, 'r') as f:
        desc = f.read()
        description = json.loads(desc)
    url = description['url']
    browser.get(url)
    #todo : get size chart

browser.close()