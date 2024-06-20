#!/bin/bash
#this script expects as input a folder full of downloaded folders (from google drive)

#########boilerplate code for args
if [ ! $# -eq 4 ]
  then
    echo "Error; the format is process_downloads.sh --in FOLDER --out FOLDER"
    exit 2
fi

while [ -n "$1" ]; do # while loop starts
    case "$1" in
    --in) input_folder="$2"
        input_folder_bn=$(basename -- "${input_folder}")
        shift
        ;;
    --out) out_dir="$2"
        shift
        ;;
    --)
        shift # The double dash makes them parameters
        break
        ;;
    *) echo "Error; option $1 not recognized. The format is process_downloads.sh --in FOLDER --out FOLDER"
        exit 2 
        ;;
    esac
    shift
done

current_dir=$(pwd)
stamp=$(date +%s)
mkdir -p "${out_dir}/VIDEOS_${stamp}"
mkdir -p "${out_dir}/VIDEOS_(4K)_${stamp}"
mkdir -p "${out_dir}/IMAGES_${stamp}"
mkdir -p "${out_dir}/RAW_IMAGES_${stamp}"


downloads_fn="downloads_${timestamp}_${input_folder_bn}.txt"

ls "${input_folder}" > "util/${downloads_fn}" #there should only be directories in here! 
readarray -t folders < "util/${downloads_fn}"
for fold in "${folders[@]}"
do 
    fold_full_path="${input_folder}/${fold}"
    if [  -d "${fold_full_path}" ]; then
        cd "${fold_full_path}"
        cd "${current_dir}"
        python util/split_images_and_video_skip_raw.py --media_folder "${fold_full_path}" --out_dir "${out_dir}" --timestamp "${stamp}"
    else 
        echo "${fold_full_path} is not a directory"
    fi
done 

rm "util/${downloads_fn}"


