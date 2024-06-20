import get_folder_bboxes_video
import argparse
import os
from pathlib import Path

def get_bboxes(work_folders_dir, extracted_bboxes_folder):
	wfd = work_folders_dir
	bf = extracted_bboxes_folder

	wf_list = next(os.walk(wfd))[1]
	for wf in wf_list:
		if "(VIDEO)" in wf:
			wf = str(Path(wfd, wf))
			get_folder_bboxes_video.get_bboxes(wf, bf)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--work_folders_dir", required = True)
    ap.add_argument("--extracted_bboxes_folder", required = True)
    args = vars(ap.parse_args())

    wfd = args['work_folders_dir']
    bf = args['extracted_bboxes_folder']

    get_bboxes(wfd, bf)

	

