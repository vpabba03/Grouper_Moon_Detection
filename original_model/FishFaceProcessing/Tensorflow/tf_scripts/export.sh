#!/bin/bash

usage()
{
    echo
    echo "Usage: ./export.sh <model_name> <config_file> <NUM_TRAIN_STEPS>"
    echo
    echo "Example: sh train.sh faster_rcnn_resnet101_joe_data_coco faster_rcnn_resnet101_coco_train_joe.config 20000"
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
CHECKPOINT_PREFIX=${MODEL_DIR}/model.ckpt-${NUM_TRAIN_STEPS}
OUTPUT_DIR=exported_models/$1

# clear old exported model
rm -rf ${OUTPUT_DIR}

PYTHONPATH=`pwd`/models/research:`pwd`/models/research/slim \
    python3 ./models/research/object_detection/export_inference_graph.py \
            --input_type=image_tensor \
            --pipeline_config_path=${PIPELINE_CONFIG_PATH} \
            --trained_checkpoint_prefix=${CHECKPOINT_PREFIX} \
            --output_directory=${OUTPUT_DIR}
