import numpy as np
import pandas as pd
import argparse
import imutils
import time
import cv2
import shutil
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("-dat", "--detectionsdatawithids", required=True,
    help="csv with bounding boxes and object ids")
ap.add_argument("-imgfold", "--folderwithimgs", required=True,
    help="folder of images")
ap.add_argument("-outdir", "--output_directory", required = False, help = 'output directory to save images')
ap.add_argument("-outtempdir", "--output_temp_directory", required = True, help = 'output directory to save temp images')
ap.add_argument("-boxesdir", "--bboxes_directory", required = True, help = "directory for bboxes")
args = vars(ap.parse_args())

#buffer parameters assume 4fps

def make_to_write(has_detects, buffer = 13): #buffer is a little over 3 seconds long in both directions, left and right
    #to_write is a list that says to save the frame or not
    #should save the frame if it's got a detection, 
    #OR if buffer frames ahead and behind has detections
    to_write = [ 
    True if (
        (has_detects[i] is True) or 
        any(
            has_detects[max(0,(i - buffer)):min(len(has_detects),i + buffer)]
            )
        ) 
    else False 
    for i in range(len(has_detects))
    ]
    return(to_write)

def annotate_frame(frame, frame_img, detects_df, has_detect_list, save_box = True):

    #get all the dataframe of detections for this video frame
    frame_detects = df.loc[frame]

    # loop over the tracked objects in the frame
    for detect_num, row in frame_detects.iterrows():
        if detect_num == 0:
            detected = False
            continue #break would also work, since when detect_num == 0, the for-loop is length 1
        boxID = df.index.get_loc((frame,detect_num))
        objectID = int(row['obj_id'])
        ymin = int(row['ymin'])
        ymax = int(row['ymax'])
        xmin = int(row['xmin'])
        xmax = int(row['xmax'])
        centroid = (int(row['xmean']), int(row['ymean']))
        top_left = (xmin, ymin)
        bottom_right = (xmax, ymax)
        if save_box:
            box_fn = str(Path(args['bboxes_directory'], str(frame) + "_ID" + str(objectID) + "_box" + str(boxID) + ".jpg"))
            box_img = img[ymin:ymax, xmin:xmax]
            cv2.imwrite(box_fn, box_img)

        # draw both the ID of the object and the centroid of the
        # object on the output frame
        fish_id_text = "ID {}".format(objectID)
        box_id_text = "BB {}".format(boxID)
        cv2.putText(frame_img, fish_id_text, (centroid[0] - 10, centroid[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
        cv2.putText(frame_img, box_id_text, (centroid[0] - 20, centroid[1] + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
        cv2.circle(frame_img, center = (centroid[0], centroid[1]), radius = 4, color = (0, 255, 0), thickness = -1)
        cv2.rectangle(frame_img, top_left, bottom_right, color = (0, 255, 0), thickness = 1)
        detected = True
    has_detect_list.append(detected)

def add_timestamp_to(frame_img, text = "--:--:--"):
    cv2.putText(frame_img, text, (10,60),
        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
    cv2.rectangle(frame_img, (0,0), (320,90), color = (0, 255, 0), thickness = 3)


df = pd.read_csv(args['detectionsdatawithids'], index_col = [0,1])
imgfold = args['folderwithimgs']
frames = set(df.index.get_level_values(0))
frames = list(frames)
frames.sort()

has_detects = [] #should be have length number of frames, with true or false on whether a frame has detections

#iterate through frames first time to generate frames for longer video
for frame_num, frame in enumerate(frames):
    fn = str(Path(imgfold, str(frame) + '.jpg'))
    img = cv2.imread(fn)
    img_copy = cv2.imread(fn)
    if img is None:
        sys.exit('failed to load image: %s' % image_path)
    #img = img[..., ::-1]  # BGR to RGB
    annotate_frame(frame, frame_img = img_copy, detects_df = df, has_detect_list = has_detects, save_box = True)

    out_fn_temp = str(Path(args['output_temp_directory'], "img_" + str(frame_num) + ".jpg"))
    cv2.imwrite(out_fn_temp, img_copy)

to_write = make_to_write(has_detects, buffer = 13)
keep_num = 0

#iterate through frames first time to generate frames for shortened video
#use as a marker to detect change
previous_to_write = False
for frame_num, frame in enumerate(frames):
    fn = str(Path(imgfold, str(frame) + '.jpg'))
    img = cv2.imread(fn)
    img_copy = cv2.imread(fn)
    if img is None:
        sys.exit('failed to load image: %s' % image_path)
    #img = img[..., ::-1]  # BGR to RGB

    if to_write[frame_num]:
        annotate_frame(frame, frame_img = img_copy, detects_df = df, has_detect_list = [], save_box = True)
        secs = frame_num * 0.25 #assumes 4 fps
        ts = str(time.strftime("%H:%M:%S", time.gmtime(secs)))
        add_timestamp_to(frame_img = img_copy, text = ts)
        out_fn_temp = str(Path(args['output_temp_directory'], "img_keep" + str(keep_num) + ".jpg"))
        cv2.imwrite(out_fn_temp, img_copy)
        keep_num = keep_num + 1
        previous_to_write = True
    else:
        if previous_to_write:
            black_frame = np.zeros(img_copy.shape)
            ts = "--:--:--"
            add_timestamp_to(frame_img = black_frame, text = ts)
            for i in range(8): #adds 2 seconds of blackness
                out_fn_temp = str(Path(args['output_temp_directory'], "img_keep" + str(keep_num) + ".jpg"))
                cv2.imwrite(out_fn_temp, black_frame)
                keep_num = keep_num + 1
        previous_to_write = False


                           

bboxes_to_zip = args['bboxes_directory']
bboxes_zip_fn = bboxes_to_zip

try: 
    shutil.make_archive(bboxes_zip_fn, 'zip', bboxes_to_zip)
    zip_success = True
except:
    zip_success = False

if zip_success:
    shutil.rmtree(bboxes_to_zip)