# USAGE
# python object_tracker.py --prototxt deploy.prototxt --model res10_300x300_ssd_iter_140000.caffemodel

# import the necessary packages
from pyimagesearch.centroidtracker_modif import CentroidTracker
from imutils.video import VideoStream
import numpy as np
import pandas as pd
import argparse
import imutils
import time
import cv2
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("-md", "--maxDisappeared", default=4,
	help="maximum number of disappeared frames until object is deregistered")
ap.add_argument("-dat", "--detectionsdata", required=True,
	help="csv with bounding boxes")
ap.add_argument("-outdir", "--output_directory", required = True, help = 'output directory to save csv')
args = vars(ap.parse_args())

#example usage python object_tracker_imgs.py -dat '/home/semmenslab/Documents/Drewstuff/fishface/playground/GP041142_detections_output_sorted.csv' -outdir '/home/semmenslab/Documents/Drewstuff/fishface/playground' 



df = pd.read_csv(args['detectionsdata'], index_col = [0,1])
df = df.sort_index(level = 'img_frame', ascending = True)
more_cols = ['score','xmean','ymean','obj_id']
detec_cols = ['xmin', 'ymin', 'xmax', 'ymax']
df_tracker = pd.DataFrame(df, columns = detec_cols + more_cols)
df = df[detec_cols]

# initialize our centroid tracker and frame dimensions
ct = CentroidTracker(maxDisappeared = int(args['maxDisappeared']))
frames = df.index.get_level_values(0)
# loop over the frames in the csv 
for frame in frames:
	#get the list of bounding box rectangles
	num_rects = []
	frame_detects = df.loc[frame]
	for detect_num, row in frame_detects.iterrows():
		if int(detect_num) == 0:
			pass
		else:
			rect = np.array(row).astype('int')
			num_rect = (int(detect_num), rect)
			num_rects.append(num_rect)
			

	# update our centroid tracker using the computed set of bounding
	# box rectangles
	detect_num, objects = ct.update(num_rects)


	for key, value in objects.items():
		if key not in detect_num:
			continue
		else:
			df_tracker.loc[(frame, detect_num[key]), 'obj_id'] = key
			df_tracker.loc[(frame, detect_num[key]),'xmean'] = value[0]
			df_tracker.loc[(frame, detect_num[key]),'ymean'] = value[1]

output_dir = args['output_directory']
fn = str(Path(output_dir, Path(args['detectionsdata']).stem)) + '_with_obj_id.csv'
df_tracker.to_csv(fn)

