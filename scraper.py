from selenium import webdriver
import requests
import json
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

def get_reviews(spu):
    url ='https://us.shein.com/goods_detail/getCommentInfoByAbc?spu=' + spu + '&goods_id=&page=1&limit=3&sort=&size=&is_picture='
    comments = []
    initial_response = requests.get(url = url)
    loaded_initial_response = json.loads(initial_response.text)
    max_length = loaded_initial_response['info']['allTotal']
    pages = math.ceil(max_length/3)
    for i in range(1, pages+1):
        url ='https://us.shein.com/goods_detail/getCommentInfoByAbc?spu=' + spu + '&goods_id=&page=' + str(i) + '&limit=3&sort=&size=&is_picture='
        response = requests.get(url = url)
        reviews = json.loads(response.text)
        comments.extend(reviews['info']['commentInfo'])
        if not i % 100:
            print("{}/{} pages".format(i, pages + 1))
        break #todo: get rid of to run everything
    filename = "data/reviews/" + spu + '.txt'
    with open(filename, 'w') as f:
        json.dump(comments, f)
    return filename

# Specifying incognito mode
option = webdriver.ChromeOptions()
option.add_argument("--incognito")
browser = webdriver.Chrome(executable_path='chromedriver', chrome_options=option)

base_url = 'https://us.shein.com/Women-Tops-c-2223.html?icn=women-tops&ici=us_tab01navbar02menu03&srctype=category&userpath=category%3EWOMEN%3ECLOTHING%3ETops&scici=navbar_2~~tab01navbar02menu03~~2_3~~real_2223~~~~0~~0'
browser.get(base_url)
all_tops_inventory = {}
all_tops_description = {}

total_items = browser.find_element_by_class_name("header-sum").text.split(" ")[0]
pages = math.ceil(int(total_items)/120) #120 items per page
for page in range(1, pages + 1):
    url = base_url
    if page != 1:
        url = base_url + '&page=' + str(page)
    inventory = get_inventory(url)
    all_tops_inventory = {**all_tops_inventory, **inventory}
    break # todo: get rid of to run everything

top = "https://us.shein.com/Ditsy-Floral-Tie-Front-Puff-Sleeve-Crop-Top-p-695348-cat-2223.html?scici=navbar_2~~tab01navbar02menu03~~2_3~~real_2223~~~~0~~0"
all_tops_inventory[top] = 0
# todo: get rid of above to run everything
for top in all_tops_inventory:
    browser.get(top)
    unparsed_spu = browser.find_element_by_class_name("j-expose__common-reviews__list-item").get_attribute('data-expose-id')
    spu = unparsed_spu.split('-')[3]

    reviews_filename = get_reviews(spu)

    name = browser.find_element_by_class_name("product-intro__head-name").text
    unparsed_main_pictures = browser.find_elements_by_class_name("product-intro__main-item")
    main_pic_urls = []
    for pic in unparsed_main_pictures:
        pic_url = pic.find_element_by_class_name("j-verlok-lazy").get_attribute('data-src')[2:]
        main_pic_urls.append(pic_url)

    desc = browser.find_elements_by_class_name("product-intro__description-table-item")
    clothing_desc = {}
    for li in desc:
        key = li.find_element_by_class_name("key").get_attribute("innerHTML")
        val = li.find_element_by_class_name("val").get_attribute("innerHTML")
        clothing_desc[key[:-1]] = val
    all_tops_description[spu] = {}
    all_tops_description[spu]['name'] = name
    all_tops_description[spu]['clothing_desc'] = clothing_desc
    all_tops_description[spu]['product_pcs'] = main_pic_urls
    all_tops_description[spu]['review_filename'] = reviews_filename
    break #todo: get rid of to run everything
filename = 'data/desc.txt'
with open(filename, 'w') as f:
    json.dump(all_tops_description, f)
browser.close()

'''
todo: size chart
'''
