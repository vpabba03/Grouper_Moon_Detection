import pandas as pd 
import argparse
import os
from os import listdir
from pathlib import Path
import shutil
import time

def combine_bboxes(bboxes_to_combine_dir, dest_dir): #dest_dir should have an existing csv of bboxes and images; can make one if there is not
    #csvs = [os.path.join(r, f) for r, d, f in os.walk(bboxes_to_combine_dir) if os.path.splitext(f) == '.csv']
    bboxes_csvs = []
    bboxes_imgs = []
    for root, dirs, files in os.walk(bboxes_to_combine_dir):
        for f in files:
            if os.path.splitext(f)[1] == '.csv':   
                bboxes_csvs.append(os.path.join(root, f))
            elif os.path.splitext(f)[1] == '.jpg':
                bboxes_imgs.append(os.path.join(root, f))

    bboxes_dfs = [pd.read_csv(fn) for fn in bboxes_csvs]
    all_bboxes_df = pd.concat(bboxes_dfs)

    current_bboxes_csv = os.path.join(dest_dir, 'grouper_bboxes_record.csv')
    current_bboxes_images = os.path.join(dest_dir, 'bboxes')
    Path.mkdir(Path(current_bboxes_images), parents = True, exist_ok = True)
    try:
        current_bboxes_df = pd.read_csv(current_bboxes_csv)
        current_bboxes_df = pd.concat([all_bboxes_df, current_bboxes_df])
        dups_bool = current_bboxes_df.duplicated()
        dups = current_bboxes_df[dups_bool]
        if dups.shape[0] > 0:
            print(str(dups.shape[0]) + " duplicate rows detected; for instance this row is duplicated:")
            print(dups.iloc[0])
            print("To continue press y; press any other key to abort")
            cont = input()
            if cont == 'y' or cont == "Y":
                pass
            else:
                return None
        current_bboxes_df.to_csv(current_bboxes_csv, index = False)
    except:
        all_bboxes_df.to_csv(current_bboxes_csv, index = False)

    for bbox in bboxes_imgs:
        shutil.copy(src = bbox, dst = current_bboxes_images)
                
                
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--bboxes_to_combine_dir", required = True)
    ap.add_argument("--dest_dir", required = True)
    args = vars(ap.parse_args())
    bboxes_to_combine_dir = args['bboxes_to_combine_dir']
    dest_dir = args['dest_dir']
    combine_bboxes(bboxes_to_combine_dir, dest_dir)
    
    

