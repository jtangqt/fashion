from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from os import listdir
from os.path import isfile, join
import requests
import json
import time
import math

def get_inventory(url):
    tops_url = {}
    browser.get(url)
    elems = browser.find_elements_by_class_name("c-goodsitem")
    for elem in elems:
        href = elem.find_element_by_css_selector("a[href*='/']").get_attribute('href')
        if href not in tops_url:
            tops_url[href] = 0
    return tops_url

def get_reviews(spu, filename):
    split = 50
    url = 'https://us.shein.com/goods_detail_nsw/getCommentInfoByAbc?spu=' + spu + '&goods_id=&page=1&limit=' + str(split) + '&sort=&size=&is_picture='
    initial_response = requests.get(url = url)
    loaded_initial_response = json.loads(initial_response.text)
    max_length = loaded_initial_response['info']['allTotal']
    print("Info: got {} number of comments for {}".format(max_length, spu))
    pages = math.ceil(max_length/split)
    comments = loaded_initial_response['info']['commentInfo']
    for i in range(1, pages+1):
        url ='https://us.shein.com/goods_detail_nsw/getCommentInfoByAbc?spu=' + spu + '&goods_id=&page=' + str(i) + '&limit=' + str(split) +'&sort=&size=&is_picture='
        response = requests.get(url = url)
        reviews = json.loads(response.text)
        comments.extend(reviews['info']['commentInfo'])
        if not i % 10:
            print("Info: copying {}/{} review pages".format(i, pages + 1))
    with open(filename, 'w') as f:
        json.dump(comments, f)
        print("Info: succesfully saved comments into", filename)

def get_all_inventory(present, all_tops_inventory):
    bad = {}
    for top in all_tops_inventory:
        browser.get(top)
        try:
            unparsed_spu = browser.find_element_by_class_name("j-expose__common-reviews__list-item").get_attribute('data-expose-id')
        except NoSuchElementException:
            print("Info: got no such element exception, retrying after 5 seconds")
            time.sleep(5)
            try:
                unparsed_spu = browser.find_element_by_class_name("j-expose__common-reviews__list-item").get_attribute('data-expose-id')
            except NoSuchElementException:
                print("Warning: no such element exception for item at url:", top)
                bad[top] = 0
                continue
        spu = unparsed_spu.split('-')[3]
        name = browser.find_element_by_class_name("product-intro__head-name").text
        filename = 'data/' + spu + '.txt'
        reviews_filename = "data/reviews/" + spu + '.txt'
        if spu not in present:
            print("Info: getting information from item: {}".format(name))
            get_reviews(spu, reviews_filename)
        else:
            print("Info: skipping getting reviews for item: {}, already exists".format(name))

        unparsed_main_pictures = browser.find_elements_by_class_name("product-intro__main-item")
        main_pic_urls = []
        for pic in unparsed_main_pictures:
            pic_url = pic.find_element_by_class_name("j-verlok-lazy").get_attribute('data-src')[2:]
            main_pic_urls.append(pic_url)
        if len(main_pic_urls) > 0:
            print("Info: successfully saved main pictures")

        desc = browser.find_elements_by_class_name("product-intro__description-table-item")
        clothing_desc = {}
        for li in desc:
            key = li.find_element_by_class_name("key").get_attribute("innerHTML")
            val = li.find_element_by_class_name("val").get_attribute("innerHTML")
            clothing_desc[key[:-1]] = val
        if len(clothing_desc) > 0:
            print("Info: successfully saved descriptions")

        model_stats = {}
        try:
            price_unparsed = browser.find_element_by_class_name("product-intro__head-price").find_element_by_class_name("original").get_attribute("innerHTML")
            price = float(price_unparsed.split("$")[1])
        except:
            price_unparsed = browser.find_element_by_class_name("product-intro__head-price").find_element_by_class_name("discount").get_attribute("innerHTML")
            price = float(price_unparsed.split("$")[1])
        try:
            model_description = browser.find_element_by_class_name("product-intro__sizeguide-summary-list")
            model_info = model_description.find_elements_by_css_selector("div")
            for info in model_info:
                if len(info.find_elements_by_css_selector("div")) != 0:
                    continue
                key = info.get_attribute('innerHTML').split(":")[0].strip()
                value = info.find_element_by_css_selector("span").get_attribute("innerHTML")
                model_stats[key] = value
        except:
            print("Info: no model information for item")

        description = {'name': name,
                       'url': top,
                       'clothing_desc': clothing_desc,
                       'price': price,
                       'product_pcs': main_pic_urls,
                       'review_filename': reviews_filename,
                       'model_stats': model_stats }
        with open(filename, 'w') as f:
            json.dump(description, f)
            print("Info: successfully saved item information into file:", filename)
        present[spu] = 0
    return bad


# Specifying incognito mode
option = webdriver.ChromeOptions()
option.add_argument("--incognito")
browser = webdriver.Chrome(executable_path='chromedriver', chrome_options=option)

base_url = 'https://us.shein.com/Women-Tops-c-2223.html?icn=women-tops&ici=us_tab01navbar02menu03&srctype=category&userpath=category%3EWOMEN%3ECLOTHING%3ETops&scici=navbar_2~~tab01navbar02menu03~~2_3~~real_2223~~~~0~~0'
browser.get(base_url)
all_tops_inventory = {}
bad = {}

data_folder = 'data'
onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
present = {f.split(".")[0]: 0 for f in onlyfiles}

total_items = browser.find_element_by_class_name("header-sum").text.split(" ")[0]
pages = math.ceil(int(total_items)/120) #120 items per page
for page in range(1, pages + 1):
    url = base_url
    if page != 1:
        url = base_url + '&page=' + str(page)
    inventory = get_inventory(url)
    all_tops_inventory = {**all_tops_inventory, **inventory}
    break # todo: get rid of to run everything

bad = get_all_inventory(present,all_tops_inventory)
bad_2 = get_all_inventory(present, bad)
print(bad_2)

browser.close()

