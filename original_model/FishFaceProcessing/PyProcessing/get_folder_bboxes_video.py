import pandas as pd
import argparse
import os
from os import listdir
from pathlib import Path
import shutil
import time
import zipfile
import logging
import sys

# logger = logging.getLogger('get_folder_bboxes_video')
# console_printer = logging.StreamHandler(sys.stdout)
# log_writer = logging.StreamHandler('get_folder_bboxes_video.log')

# only_message = logging.Formatter('%(message)s')

# logger.setLevel(logging.DEBUG)
# console_printer.setLevel(logging.DEBUG)
# log_writer.setLevel(logging.DEBUG)

# logging.basicConfig(format = '%(message)s')
# console_printer.setFormatter(only_message)
# log_writer.setFormatter(only_message)

# logger.addHandler(console_printer)
# logger.addHandler(log_writer)


def get_bboxes_from_all_volunteers(all_voluns, extracted_bboxes_folder, force):
    volunteer_folders = next(os.walk(all_voluns))[1]
    for vf in volunteer_folders:
        get_bboxes_from_volunteer_folder(os.path.join(all_voluns,vf), extracted_bboxes_folder, force)


def get_bboxes_from_volunteer_folder(volunteer_folder, extracted_bboxes_folder, force):
    volunteer_folder = os.path.abspath(volunteer_folder)
    volunteer_name = Path(volunteer_folder).name
    media_folders = next(os.walk(volunteer_folder))[1]
    for mf in media_folders:
        get_bboxes_from_media_folder(os.path.join(volunteer_folder,mf), extracted_bboxes_folder, volunteer_name, force)

def get_bboxes_from_media_folder(media_folder, extracted_bboxes_folder, volunteer_name, force):
    mf = media_folder
    parent_folders = Path(media_folder).name
    work_folders = next(os.walk(mf))[1]
    for wf in work_folders:
        get_bboxes_from_work_folder(os.path.join(mf, wf), extracted_bboxes_folder, parent_folders, volunteer_name, force)


def get_bboxes_from_work_folder(work_folder, extracted_bboxes_folder, parent_folders, volunteer_name, force):



    wf = work_folder
    vid_name = Path(work_folder).name

    print("Extracting from folder " + wf + " from volunteer " + volunteer_name + "...")

    #have to pick the file from which to extract the bboxes from. order of priority:
        # 1. files I added with drew_finished
        # 2. files that are named based on the format
        # 3. anything else that says "finished"
        # 4. other bboxes


    fns_in_wf = os.listdir(wf)
    finished_fns = [fn for fn in fns_in_wf if
                        (
                        (("finished" in fn) or ("Finished" in fn)) and ("drew_finished" not in fn)
                        )
                    ]
    drew_finished_fns = [fn for fn in fns_in_wf if ("drew_finished" in fn)]
    if len(drew_finished_fns) > 0:
        drew_finished_xlsx = str(Path(wf, drew_finished_fns[0]))
    else:
        drew_finished_xlsx = "XXXXXXXX"
    if len(finished_fns) == 1:
        other_voln_finished_fn = str(Path(wf, finished_fns[0]))
    if len(finished_fns) > 1:
        print("====================================")
        print("Multiple finished files detected, namely:")
        print(finished_fns)
        other_voln_finished_fn = str(Path(wf, finished_fns[1]))
        print("Software is using ", other_voln_finished_fn)
        if force:
        	print('---force flag passed, so moving on')
        	print("====================================")
        elif other_voln_finished_fn[-5:] == '.xlsx':
        	print('Assuming the excel file is the right one, so moving on')
        	print('================================')
        else:
	        print("Press any key to continue")
	        print("====================================")
	        input()
    else:
        other_voln_finished_fn = "XXXXXXXX"



    bboxes_finished_csv = vid_name + "_bboxes_to_keep_finished.csv"
    bboxes_finished_csv = str(Path(wf, bboxes_finished_csv))
    bboxes_finished_xlsx = vid_name + "_bboxes_to_keep_finished.xlsx"
    bboxes_finished_xlsx = str(Path(wf, bboxes_finished_xlsx))
    bboxes_all_csv = vid_name + "_detections_output_with_obj_id.csv"
    bboxes_all_csv = str(Path(wf, bboxes_all_csv))
    bboxes_images_dir = str(Path(wf, "bboxes"))
    bboxes_images_zip = str(Path(wf, "bboxes.zip"))
    metadat_txt = vid_name + "_metadata.txt"
    metadat_txt = str(Path(wf, metadat_txt))


    extract_path = str(Path(bf, volunteer_name + "_--_" + parent_folders + "_--_" + vid_name))
    Path.mkdir(Path(extract_path), parents = True, exist_ok = True)

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

    def mark_no_bboxes():
        no_files = "no_bboxes_made_for_" + vid_name
        no_files = str(Path(extract_path, no_files))
        print("No bboxes found in " + wf)
        open(no_files, 'a').close()
        return None

    if not os.path.exists(metadat_txt):
        print("Metadata file should be named " + Path(metadat_txt).name + "...")
        metadats = [fn for fn in next(os.walk(wf))[2] if ("_metadata.txt" in fn)]
        metadat_txt = metadats[0]
        print("...trying instead " + metadat_txt)
        metadat_txt = str(Path(wf, metadat_txt))

    if not os.path.exists(bboxes_all_csv):
        print("Detections file should be named " + Path(bboxes_all_csv).name + "...")
        detects = [fn for fn in next(os.walk(wf))[2] if ("_detections_output_with_obj_id.csv" in fn)]
        try:
            bboxes_all_csv = detects[0]
        except IndexError:
            print("No detections file... Processing the video " + wf + " probably failed.")
            mark_no_bboxes()
            print("--------------------------")
            return None
        print("...trying instead " + bboxes_all_csv)
        bboxes_all_csv = str(Path(wf, bboxes_all_csv))



    if not os.path.exists(bboxes_images_dir) and not os.path.exists(bboxes_images_zip):
        mark_no_bboxes()
        print("--------------------------")
        return None
    elif not os.path.exists(bboxes_images_dir):
        with zipfile.ZipFile(bboxes_images_zip, 'r') as zip_ref:
            zip_ref.extractall(str(Path(wf, 'bboxes'))) #should be called #bboxes



    try:
        with open(metadat_txt) as meta:
            for line in meta:
                if "creation_time" in line:
                    creation_time = line.split("=")[1].rstrip("\n")
                    break
                else:
                    creation_time = None
    except:
        import pdb; pdb.set_trace()


    #choose the bboxes file

    if os.path.isfile(drew_finished_xlsx):
        has_bboxes = check_if_bboxes(drew_finished_xlsx)
        bboxes_dat = read_csv_excel(drew_finished_xlsx)
    elif os.path.isfile(bboxes_finished_xlsx):
        has_bboxes = check_if_bboxes(bboxes_finished_xlsx)
        bboxes_dat = read_csv_excel(bboxes_finished_xlsx)
    elif os.path.isfile(bboxes_finished_csv):
        has_bboxes = check_if_bboxes(bboxes_finished_csv)
        bboxes_dat = read_csv_excel(bboxes_finished_csv)
    elif os.path.isfile(other_voln_finished_fn):
        has_bboxes = check_if_bboxes(other_voln_finished_fn)
        bboxes_dat = read_csv_excel(other_voln_finished_fn)
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
        mark_no_bboxes()
        print("--------------------------")
        return None

    #desired output: a folder with the same name as what I have,
    #moved to the extracted bboxes directory, but with only the bboxes that were kept, and a csv listing them, with metadata.

    bboxes_copied_here = str(Path(extract_path, "bboxes"))

    Path.mkdir(Path(bboxes_copied_here), parents = True, exist_ok = True)

    bboxes_fns = listdir(bboxes_images_dir)
    bbox_weirds = [bbox for bbox in bboxes_fns if ").jpg" in bbox]
    bboxes_fns = [bbox for bbox in bboxes_fns if ").jpg" not in bbox]

    if len(bbox_weirds) > 0:
        print("!!!!!!!!!!#############!!!!!!!!!!!")
        print("There are duplicate images in bboxes folder?")
        print(bbox_weirds)
        print("Ignoring...")
    try:
        bbox_nums = [int(bbox.rsplit(sep = "_box")[1][:-4]) for bbox in bboxes_fns if ").jpg" not in bbox]
    except ValueError:
        print("!!!!!!!!!!#############!!!!!!!!!!!")
        print("ValueError! Check filenames for bboxes in " + wf)
        print("They don't seem to all end in integers! Quitting...")
        raise

    if len(bbox_nums) != len(bboxes_fns):
        print("Different numbers of bboxes and valid bbox numbers!")
        raise RuntimeError

    bboxes_dict = dict(zip(bbox_nums, bboxes_fns))

    bboxes_extracted_list = []
    metadat_cols = ['bbox_name_(auto)', 'created_date_(auto)', 'parent_folders_(auto)', 'volunteer_name_(auto)', 'location', 'diver', 'year', 'month', 'day', 'rough_time_of_day', 'video_comments', 'bbox_comments', 'tagged', 'same_as_other_box', 'laser','phase','xmin', 'ymin', 'xmax', 'ymax', 'score', 'obj_id']
    bboxes_all_df = pd.read_csv(bboxes_all_csv)

    for ind, row_to_keep in bboxes_dat.iterrows():
        extracted_row = {}
        try:
            box_num = int(row_to_keep['best_bboxes'])
        except ValueError:
            #if row_to_keep['best_bboxes'] == 'X':
            #    import pdb; pdb.set_trace()
            non_int = str(row_to_keep['best_bboxes'])
            print("!!!!!!!###########################!!!!!!!!")
            print("Non-integer value detected:")
            print(non_int + " detected in " + wf + " on row " + str(ind))
            if ind == bboxes_dat.shape[0] - 1 and len(bboxes_extracted_list) == 0:
                print("!!!!!!!#############################!!!!!!!")
                print("Found only non-integer values in " + wf)
                print("Treating as no bboxes")
                mark_no_bboxes()
                print("--------------------------")
                return None
            else:
                continue
        try:
            extracted_row['bbox_name_(auto)'] = bboxes_dict[box_num]
        except KeyError:
            print("!!!!!!!#############################!!!!!!!!")
            print("There was a typo!")
            print("Box " + str(box_num) + " was not an actual bbox, in " + wf)
            if force:
            	print("--force flag was passed, so skipping...")
            	continue
            else:
	            print("Input the correct value to fix it. Or, press c to skip it. Or, press q to exit.")
	            box_num = input()
	            if box_num == "c" or box_num == "C":
	                continue
	            try:
	                box_num = int(box_num)
	            except: #from pressing q, or any other non-integer input
	                quit()
	            try:
	                extracted_row['bbox_name_(auto)'] = bboxes_dict[box_num]
	            except KeyError:
	                "That number was also not a bbox. Quitting..."
	                raise
        if creation_time:
            extracted_row['created_date_(auto)'] = creation_time
        extracted_row['parent_folders_(auto)'] = parent_folders.replace("_--_", "/")
        extracted_row['volunteer_name_(auto)'] = volunteer_name
        try: #i forgot to add the tagged ones in!
        	comments = row_to_keep['comments']
        	if 'laser' in comments or 'LASER' in comments or 'Laser' in comments:
        		print("...for bbox", box_num, "comment reads", comments)
        		print("assuming this is for lasers, not fish faces. skipping bbox", box_num, "...")
        	extracted_row['bbox_comments'] = comments
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


    bboxes_extracted_csv = vid_name + "_bboxes_extracted.csv"
    bboxes_extracted_csv = str(Path(extract_path, bboxes_extracted_csv))


    bboxes_extracted_df.to_csv(bboxes_extracted_csv, index = False)
    for bbox in bboxes_to_copy:
        shutil.copy(src = bbox, dst = bboxes_copied_here)
    print("...success")
    print("--------------------------")
    return None




if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--all_voluns", required = True)
    ap.add_argument("--extracted_bboxes_folder", required = True)
    ap.add_argument("--force", action = 'store_true')
    args = vars(ap.parse_args())

    all_voluns = args['all_voluns']
    bf = args['extracted_bboxes_folder']
    force = args['force']

    if force:
    	print("--force flag passed, which will skip errors. Press q to quit or any other key to continue")
    	cont = input()
    	if cont == 'q' or cont == 'Q':
    		quit()

    get_bboxes_from_all_volunteers(all_voluns, bf, force)






