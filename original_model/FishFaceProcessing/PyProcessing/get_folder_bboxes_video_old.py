import pandas as pd 
import argparse
import os
from os import listdir
from pathlib import Path
import shutil
import time
import zipfile

def get_bboxes(work_folder, extracted_bboxes_folder):
    wf = work_folder
    bf = extracted_bboxes_folder
    wf_stem = os.path.basename(wf)
    fn_components = wf_stem.split("_--_")
    volunteer_name = fn_components[0]
    vid_name = fn_components[-1]
    parent_folders = "_--_".join(fn_components[1:-1])


    bboxes_finished_csv = vid_name + "_bboxes_to_keep_finished.csv"
    bboxes_finished_csv = str(Path(wf, bboxes_finished_csv))
    bboxes_finished_xlsx = vid_name + "_bboxes_to_keep_finished.xlsx"
    bboxes_finished_xlsx = str(Path(wf, bboxes_finished_xlsx))
    bboxes_all_csv = vid_name + "_detections_output_with_obj_id.csv"
    bboxes_all_csv = str(Path(wf, bboxes_all_csv))
    bboxes_images_dir = str(Path(wf, "bboxes"))
    bboxes_images_zip = str(Path(wf, "bboxes.zip"))
    if !os.path.exists(bboxes_images_dir):
        with zipfile.ZipFile(bboxes_images_zip, 'r') as zip_ref:
            zip_ref.extractall(bboxes_images_dir)
    bboxes_extracted_csv = vid_name + "_bboxes_extracted.csv"
    bboxes_extracted_csv = str(Path(bf, wf_stem, bboxes_extracted_csv))
    metadat_txt = vid_name + "_metadata.txt"
    metadat_txt = str(Path(wf, metadat_txt))
    no_files = "no_bboxes_made_for_" + wf_stem
    no_files = str(Path(bf, wf_stem, no_files))

    with open(metadat_txt) as meta:
        for line in meta:
            if "creation_time" in line:
                creation_time = line.split("=")[1].rstrip("\n")
                break
            else: 
                creation_time = None



    def is_dat(filename):
        ext = os.path.splitext(filename)[1]
        if ext == ".xlsx" or ext == ".csv":
            return True
        else:
            return False


    def read_csv_excel(filename):
        ext = os.path.splitext(filename)[1]
        if ext == ".csv":
            df = pd.read_csv(filename)
            return df
        elif ext == ".xlsx":
            df = pd.read_excel(filename)
            return df
        else:
            return None


    def check_if_bboxes(filename):
        df = read_csv_excel(filename)
        if df is None:
            return False
        nr, nc = df.shape
        if 'best_bboxes' in list(df.columns) and nr > 0:
            return True
        else:
            return False

    if os.path.isfile(bboxes_finished_csv):
        has_bboxes = check_if_bboxes(bboxes_finished_csv)
        bboxes_dat = pd.read_csv(bboxes_finished_csv)
    elif os.path.isfile(bboxes_finished_xlsx):
        has_bboxes = check_if_bboxes(bboxes_finished_xlsx)
        bboxes_dat = pd.read_excel(bboxes_finished_xlsx)
    else:
        has_bboxes = False
        print("...No finished file in " + wf + ", so checking other files for bboxes")
        wf_files = next(os.walk(wf))[2]
        wf_files_dats = [f for f in wf_files if is_dat(f)]
        for filename in wf_files_dats:
            fn_short = filename
            filename = str(Path(wf, filename))
            has_bboxes = check_if_bboxes(filename)
            if has_bboxes:
                bboxes_dat = read_csv_excel(filename)
                print("...Bboxes found in " + fn_short)
                break

    if not has_bboxes:
        Path.mkdir(Path(bf, wf_stem), parents = True, exist_ok = True)
        print("No bboxes found in " + wf)
        open(no_files, 'a').close()
        return None
    
    #desired output: a folder with the same name as what I have, 
    #moved to the extracted bboxes directory, but with only the bboxes that were kept, and a csv listing them, with metadata.

    bboxes_copied_here = str(Path(bf, wf_stem, "bboxes"))

    Path.mkdir(Path(bboxes_copied_here), parents = True, exist_ok = True)

    bboxes_fns = listdir(bboxes_images_dir)
    bbox_nums = [int(bbox.rsplit(sep = "_box")[1][:-4]) for bbox in bboxes_fns]
    bboxes_dict = dict(zip(bbox_nums, bboxes_fns))

    bboxes_extracted_list = []
    metadat_cols = ['bbox_name_(auto)', 'created_date_(auto)', 'parent_folders_(auto)', 'volunteer_name_(auto)', 'location', 'diver', 'year', 'month', 'day', 'rough_time_of_day', 'video_comments', 'bbox_comments', 'tagged', 'same_as_other_box', 'laser','phase','xmin', 'ymin', 'xmax', 'ymax', 'score', 'obj_id']
    bboxes_all_df = pd.read_csv(bboxes_all_csv)

    for ind, row_to_keep in bboxes_dat.iterrows():
        extracted_row = {}
        try:
            box_num = int(row_to_keep['best_bboxes'])
        except ValueError:
            if ind == bboxes_dat.shape[0] - 1 and len(bboxes_extracted_list) == 0:
                print("#########################################")
                print("Found only non-integer values in " + wf_stem)
                print("Treating as no bboxes")
                Path.mkdir(Path(bf, wf_stem), parents = True, exist_ok = True)
                print("No bboxes found in " + wf)
                open(no_files, 'a').close()
                return None
            else:
                continue
        try:
            extracted_row['bbox_name_(auto)'] = bboxes_dict[box_num]
        except KeyError:
            print("#########################################")
            print("There was a typo!")
            print("Box " + str(box_num) + " was not an actual bbox, in " + wf_stem)
            print("Input the correct value to fix it, or press q to exit")
            box_num = input()
            try:
                box_num = int(box_num)
            except:
                quit()
            try:
                extracted_row['bbox_name_(auto)'] = bboxes_dict[box_num]
            except KeyError:
                "That number was also not a bbox. Quitting..."
                quit()
        if creation_time:
            extracted_row['created_date_(auto)'] = creation_time
        extracted_row['parent_folders_(auto)'] = parent_folders
        extracted_row['volunteer_name_(auto)'] = volunteer_name
        try: #i forgot to add the tagged ones in!
            extracted_row['bbox_comments'] = row_to_keep['comments']
        except:
            pass
        try:
            extracted_row['tagged'] = row_to_keep['tagged']
        except:
            pass
        try: 
            same_box_num = row_to_keep['same_as_other_box']
            extracted_row['same_as_other_box'] = bboxes_dict[same_box_num]
        except:
            pass
        try: 
            extracted_row['laser'] = row_to_keep['laser']
        except:
            pass
        try: 
            extracted_row['phase'] = row_to_keep['phase']
        except:
            pass
        extracted_row['xmin'] = bboxes_all_df.iloc[box_num]['xmin']
        extracted_row['ymin'] = bboxes_all_df.iloc[box_num]['ymin']
        extracted_row['xmax'] = bboxes_all_df.iloc[box_num]['xmax']
        extracted_row['ymax'] = bboxes_all_df.iloc[box_num]['ymax']
        extracted_row['score'] = bboxes_all_df.iloc[box_num]['score']
        extracted_row['xmean'] = bboxes_all_df.iloc[box_num]['ymean']
        extracted_row['obj_id'] = bboxes_all_df.iloc[box_num]['obj_id']

        bboxes_extracted_list.append(extracted_row)


    bboxes_extracted_df = pd.DataFrame(bboxes_extracted_list, columns = metadat_cols)
    bboxes_to_copy = bboxes_extracted_df['bbox_name_(auto)'].to_list()
    bboxes_to_copy = [str(Path(bboxes_images_dir, bbox)) for bbox in bboxes_to_copy]

    #finally, save the files

    bboxes_extracted_df.to_csv(bboxes_extracted_csv, index = False)
    for bbox in bboxes_to_copy:
        shutil.copy(src = bbox, dst = bboxes_copied_here)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--work_folder", required = True)
    ap.add_argument("--extracted_bboxes_folder", required = True)
    args = vars(ap.parse_args())

    wf = args['work_folder']
    bf = args['extracted_bboxes_folder']

    get_bboxes(wf, bf)






