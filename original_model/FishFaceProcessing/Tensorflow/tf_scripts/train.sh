#!/bin/bash

usage()
{
    echo
    echo "Usage: ./train.sh <model_name> <config_file> <NUM_TRAIN_STEPS>"
    echo
    echo "Example: sh train.sh faster_rcnn_resnet101_joe_data_coco faster_rcnn_resnet101_train_joe_coco.config 20000"
    echo
    exit
}

if [ $# -ne 3 ]; then
    usage
fi

MODEL_DIR=$1
CONFIG_FILE=$2 
NUM_TRAIN_STEPS=$3

PIPELINE_CONFIG_PATH=configs/$2

# clear old training logs
rm -rf ${MODEL_DIR}

PYTHONPATH=`pwd`/models/research:`pwd`/models/research/slim \
    python3 ./models/research/object_detection/model_main.py \
            --pipeline_config_path=${PIPELINE_CONFIG_PATH} \
            --model_dir=${MODEL_DIR} \
            --num_train_steps=${NUM_TRAIN_STEPS} \
            --sample_1_of_n_eval_samples=1 \
            --alsologtostderr
