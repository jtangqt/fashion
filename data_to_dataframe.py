from os import listdir
from os.path import isfile, join
import json
import pandas as pd




data_folder = 'data'
onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
columns = ['Item ID', 'Description', 'Price', 'Fit', 'Stars', 'Comment',
           'Member ID', 'Hips (cm)', 'Waist (cm)', 'Height (cm)', 'Bra', 'Weight (kg)', 'Bust (cm)', 'Size']
df = pd.DataFrame({}, columns=columns)

for file in sorted(onlyfiles):
    item_id = file.split(".")[0]
    if item_id == 'comments':
        continue
    print("starting file: {}".format(file))
    with open('data/' + file, 'r') as f:
        desc = f.read()
        description = json.loads(desc)
        # todo: add model stats, price
    with open('data/reviews/' + file, 'r') as f:
        reviews = f.read()
        content = json.loads(reviews)
    for review in content:
        stars = review['comment_rank'].strip()
        comment = review['content'].strip()
        member_id = review['member_id'].strip()
        member_overall_fit = review["member_overall_fit"]
        hips = review['member_size']['member_hips'].split("cm")[0].strip()
        waist = review['member_size']['member_waist'].split("cm")[0].strip()
        height = review['member_size']['member_height'].split("cm")[0].strip()
        bust = review['member_size']['member_bust'].split("cm")[0].strip()
        weight = review['member_size']['member_weight'].split("Kg")[0].strip()
        bra = review['member_size']['member_bra_size'].strip()
        size = review['size']
        values = [item_id, description['clothing_desc'], description['price'], member_overall_fit, stars, comment,
                  member_id, hips, waist, height, bra, weight, bust, size]
        member_dict = dict(zip(columns, values))
        df = df.append(member_dict, ignore_index=True)
    print("finished file: {} out of {} files".format(file, len(onlyfiles)))
    break

df.to_csv("data/comments.csv")
df.to_pickle("data/comments.pkl")
