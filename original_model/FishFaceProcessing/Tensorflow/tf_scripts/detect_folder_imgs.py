"""detect_image.py

This script is used to test my trained egohands (hand detector) models.  It is modified from the following example from TensorFlow Object Detection API:

https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
"""


import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  #disables the logging
import numpy as np
import cv2
import tensorflow as tf
import pandas as pd
import argparse
from pathlib import Path 

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

parser = argparse.ArgumentParser()
parser.add_argument("--graph", required=True)
parser.add_argument("--labels", required=True)
parser.add_argument("--imgs_dir", required=True)
parser.add_argument("--csv_dir", required=True)
args = vars(parser.parse_args())

PATH_TO_FROZEN_GRAPH = args['graph']
PATH_TO_LABELS = args['labels']
imgs_dir = args['imgs_dir']
output_dir = args['csv_dir']

def detect_image(imgs):
    # load label map
    category_index = label_map_util.create_category_index_from_labelmap(
        PATH_TO_LABELS)

    # load detection graph
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    # define input/output tensors
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # load input imgs

    boxes_df = pd.DataFrame(columns = ['img_frame','detection','ymin','xmin','ymax','xmax','score'])
    boxes_df = boxes_df.set_index(['img_frame','detection'])

    for image_path in imgs:
        img = cv2.imread(image_path)
        if img is None:
            sys.exit('failed to load image: %s' % image_path)
        img = img[..., ::-1]  # BGR to RGB

        # run inference
        with detection_graph.as_default():
            with tf.Session() as sess:
                boxes, scores, classes, _ = sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: np.expand_dims(img, 0)})

        #boxes format [ymin, xmin, ymax, xmax] in percent

        #for box in np.squeeze(boxes):
        thresh = 0.75

        image_path = str(Path(image_path).stem) + str(Path(image_path).suffix)

        s_boxes = np.squeeze(boxes)
        s_scores = np.squeeze(scores)

        ydim = img.shape[0]
        xdim = img.shape[1]

        s_boxes = [np.array([int(round(box[0] * ydim)), int(round(box[1] * xdim)), int(round(box[2] * ydim)), int(round(box[3]* xdim)), s_scores[ind]]) for ind, box in enumerate(s_boxes)]

        best_boxes = [box for ind, box in enumerate(s_boxes) if s_scores[ind] >= thresh]

        if len(best_boxes) == 0:
            boxes_df.loc[(image_path,0),:] = [None, None, None, None, None] 

        for ind, box in enumerate(best_boxes):
            boxes_df.loc[(image_path, ind+1),:] = box

        #detect_idx = pd.MultiIndex.from_tuples([(image_path_stem, ind + 1) for ind,  in enumerate(best_boxes)])

        #img_df = pd.DataFrame(best_boxes, index = detect_idx, columns = ['ymin','xmin','ymax','xmax','score'])
        #boxes_df = pd.concat([boxes_df, img_df])



        # draw the results of the detection
        # vis_util.visualize_boxes_and_labels_on_image_array(
        #     img,
        #     np.squeeze(boxes),
        #     np.squeeze(classes).astype(np.int32),
        #     np.squeeze(scores),
        #     category_index,
        #     use_normalized_coordinates=True,
        #     line_thickness=6,
        #     min_score_thresh=thresh)

        # # save the output image
        # img = img[..., ::-1]  # RGB to BGR
        # out_path = str(Path(output_dir, Path(image_path).stem)) + "_detect" + ".jpg"
        # print(out_path)
        # cv2.imwrite(out_path, img)

        # print('Output has been written to %s\n' % out_path)

    fn = str(Path(output_dir, os.path.basename(output_dir))) + '_detections_output.csv' #because because basename(output_dir) is the video name
    boxes_df.to_csv(fn)

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def main():
    to_detect = imgs_dir
    imgs = listdir_fullpath(to_detect)
    detect_image(imgs)


if __name__ == '__main__':
    main()
