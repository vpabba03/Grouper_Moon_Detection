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
parser.add_argument("--batch_size", required=True)
parser.add_argument("--cuda_visible", required=True)
args = vars(parser.parse_args())

PATH_TO_FROZEN_GRAPH = args['graph']
PATH_TO_LABELS = args['labels']
imgs_dir = args['imgs_dir']
output_dir = args['csv_dir']
batch_size = int(args['batch_size'])
try: 
    G = str(args['cuda_visible'])
except ValueError: 
    print("Non-integer cuda_visible devices; running on cpu")
    G = ""
    

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]=G

#pad_len = 150
pad_pcnt = 0.05
thresh = 0.05
if batch_size == 1:
    thresh = 0.70


def split_into_batches(some_list, batch_size):
    for i in range(0, len(some_list), batch_size):
        yield some_list[i:i+batch_size]
        
def adjust_box_locs(box, ydim, img_ind, pad_len): # box is a numpy array with 5 elts, [ymin, xmin, ymax, xmax, score] for img_concat
    ymin, xmin, ymax, xmax, score = box
    #we know that (img_ind)*(ydim) + img_ind*(pad_len) < (ymin + ymax)/2 < (img_ind + 1)*(ydim) + (img_ind + 1)*(pad_len) already
    start_reg = (img_ind)*(ydim) + img_ind*(pad_len)
    end_reg = (img_ind + 1)*(ydim) + img_ind*(pad_len)
    if ymax < end_reg:
        ymax = ymax - start_reg
    else: #ymax is in the pad region; just bring it back down to the edge
        ymax = ydim
    if ymin > start_reg:
        ymin = ymin - start_reg
    else:
        ymin = 0
    new_box = [int(ymin), int(xmin), int(ymax), int(xmax), score]
    return new_box


    
    
    
    
def detect_image(img_paths):
    img_paths.sort()
    # load label map
    category_index = label_map_util.create_category_index_from_labelmap(
        PATH_TO_LABELS)

    # load detection graph
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.io.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    # define input/output tensors
    #image_tensor = 'image_tensor:0'
    #detection_boxes = 'detection_boxes:0'
    #detection_scores = 'detection_scores:0'
    #detection_classes = 'detection_classes:0'
    #num_detections = 'num_detections:0'

    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # load input imgs
    
    img_batches = list(split_into_batches(img_paths, batch_size))

    boxes_df = pd.DataFrame(columns = ['img_frame','detection','ymin','xmin','ymax','xmax','score'])
    boxes_df = boxes_df.set_index(['img_frame','detection'])
    try:
        ydim, xdim, _ = cv2.imread(img_paths[0]).shape
    except:
        #import pdb; pdb.set_trace()
        print('oh noes')
    pad_len = int(ydim*pad_pcnt) + 1
  
    for batch in img_batches: 
        imgs = [cv2.imread(image_path) for image_path in batch]
        imgs = [img[..., ::-1] for img in imgs] #BGR to RGB
        imgs = [np.pad(img, [(0,pad_len),(0,0),(0,0)], 'constant') for img in imgs]
        try:
            img_concat = np.concatenate(imgs)
        except:
            #import pdb; pdb.set_trace()
            print('oh noes')
                
        # run inference
        with detection_graph.as_default():
            with tf.Session() as sess:
                all_boxes, all_scores, all_classes, _ = sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: np.expand_dims(img_concat, 0)})


        #boxes format [ymin, xmin, ymax, xmax] in percent
        s_all_boxes = np.squeeze(all_boxes)
        s_all_scores = np.squeeze(all_scores)
        all_ydim = img_concat.shape[0]
        all_xdim = img_concat.shape[1]
        s_all_boxes = [np.array([int(round(box[0] * all_ydim)), int(round(box[1] * all_xdim)), int(round(box[2] * all_ydim)), int(round(box[3]* all_xdim)), s_all_scores[ind]]) for ind, box in enumerate(s_all_boxes)]
        best_all_boxes = [box for ind, box in enumerate(s_all_boxes) if box[4] > thresh]

        #for box in np.squeeze(boxes):
        
        for img_ind, image_path in enumerate(batch):
            image_path_stem = str(Path(image_path).stem)
                        
            #convert s_all_boxes and boxes for this image!
                        
            best_boxes = [adjust_box_locs(box, ydim, img_ind, pad_len) for box in best_all_boxes if ( (img_ind)*(ydim + pad_len) <= (box[0] + box[2])/2 < (img_ind + 1)*(ydim + pad_len)) ] 
            #this doesn't capture the edge case of a fish being in say box 1, but the bbox extends past through pad_len into box 2 below... maybe just make pad_len bigger??

            #import pdb; pdb.set_trace()

            if len(best_boxes) == 0:
                boxes_df.loc[(image_path_stem,0),:] = [None, None, None, None, None] 

            for ind, box in enumerate(best_boxes):
                boxes_df.loc[(image_path_stem, ind+1),:] = box
        
    fn = str(Path(output_dir, os.path.basename(output_dir))) + '_detections_output.csv' #because basename(output_dir) is the video name
    boxes_df.to_csv(fn)

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def main():
    to_detect = imgs_dir
    img_paths = listdir_fullpath(to_detect)
    detect_image(img_paths)

if __name__ == '__main__':
    main()
