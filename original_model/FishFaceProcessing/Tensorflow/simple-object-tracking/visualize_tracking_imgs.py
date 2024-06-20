import numpy as np
import pandas as pd
import argparse
import imutils
import time
import cv2
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("-dat", "--detectionsdata", required=True,
	help="csv with bounding boxes")
ap.add_argument("-imgfold", "--folderwithimgs", required=True,
	help="folder of images")
ap.add_argument("-outdir", "--output_directory", required = True, help = 'output directory to save images')
ap.add_argument("-boxesdir", "--bboxes_directory", required = True, help = "directory for bboxes")
args = vars(ap.parse_args())


df = pd.read_csv(args['detectionsdata'], index_col = [0,1])
imgfold = args['folderwithimgs']
frames = df.index.get_level_values(0)
for frame_num, frame in enumerate(frames):
	#print(frame)
	frame_no_ext = str(Path(frame).stem)
	fn = str(Path(imgfold, str(frame)))
	img = cv2.imread(fn)
	img_copy = cv2.imread(fn)
	if img is None:
		#sys.exit('failed to load image: %s' % image_path)
		print('failed to load image: %s' % image_path)
		print('Moving on...')
		continue 
	#img = img[..., ::-1]  # BGR to RGB

	frame_detects = df.loc[frame]

	# loop over the tracked objects
	for detect_num, row in frame_detects.iterrows():
		if detect_num == 0:
			continue
		boxID = df.index.get_loc((frame,detect_num))
		#objectID = int(row['obj_id'])
		ymin = int(row['ymin'])
		ymax = int(row['ymax'])
		xmin = int(row['xmin'])
		xmax = int(row['xmax'])
		xmean = (xmin + xmax)/2
		ymean = (ymin + ymax)/2
		centroid = (int(xmean), int(ymean))
		top_left = (xmin, ymin)
		bottom_right = (xmax, ymax)
		#######save bbox
		################
		box_fn = str(Path(args['bboxes_directory'], str(frame_no_ext) + "_box" + str(boxID) + ".jpg"))
		box_img = img[ymin:ymax, xmin:xmax]
		cv2.imwrite(box_fn, box_img)
		##################
		###########
		#import pdb; pdb.set_trace()
		# draw both the ID of the object and the centroid of the
		# object on the output frame
		#fish_id_text = "ID {}".format(objectID)
		box_id_text = "BB {}".format(boxID)
		#cv2.putText(img_copy, fish_id_text, (centroid[0] - 10, centroid[1] - 10),
		#	cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
		cv2.putText(img_copy, box_id_text, (centroid[0] - 20, centroid[1] + 20),
			cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
		cv2.circle(img_copy, center = (centroid[0], centroid[1]), radius = 4, color = (0, 255, 0), thickness = -1)
		cv2.rectangle(img_copy, top_left, bottom_right, color = (0, 255, 0), thickness = 1)
	#out_fn = str(Path(args['output_directory'], str(frame) + "_tracked.jpg"))
	out_fn = str(Path(args['output_directory'], "img_" + str(frame_num) + ".jpg"))
	cv2.imwrite(out_fn, img_copy)
	# show the output frame
	#cv2.imshow("Frame", img)
	#key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	#if key == ord("q"):
	#	break
