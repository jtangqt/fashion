from os import listdir
from os.path import isfile, join
import json
import pandas as pd

data_folder = 'data'
onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
columns = ['Item ID', 'Stars','Comment', 'Member ID', 'Hips (cm)', 'Waist (cm)', 'Height (cm)', 'Bra', 'Weight (kg)', 'Bust (cm)']
df = pd.DataFrame({}, columns=columns)

for file in sorted(onlyfiles):
    item_id = file.split(".")[0]
    with open('data/reviews/'+file, 'r') as f:
        reviews = f.read()
        content = json.loads(reviews)
    for review in content:
        stars = review['comment_rank']
        comment = review['content']
        member_id = review['member_id']
        hips = review['member_size']['member_hips'].split("cm")[0]
        waist = review['member_size']['member_waist'].split("cm")[0]
        height = review['member_size']['member_height'].split("cm")[0]
        bust = review['member_size']['member_bust'].split("cm")[0]
        weight = review['member_size']['member_weight'].split("Kg")[0]
        bra = review['member_size']['member_bra_size']
        values = [item_id, stars, comment, member_id, hips, waist, height, bra, weight, bust]
        member_dict = dict(zip(columns, values))
        df = df.append(member_dict, ignore_index = True)
    print("finished file: {} out of {} files".format(file, len(onlyfiles)))

df.to_csv("data/comments.csv")
df.to_pickle("data/comments.pkl")
