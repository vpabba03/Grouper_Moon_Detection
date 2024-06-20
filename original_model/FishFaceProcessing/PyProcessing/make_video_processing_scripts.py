import argparse
import os
import time 

#python make_video_processing_scripts.py --to_process /media/piglet/GM\ LASER\ 19/drew_storage/separated\ media/gpu0/VIDEOS_1568956464 --dest /media/piglet/Berkley_314/drew_storage/enrolled_video_folders/ --batch_size 2 --stills /media/piglet/Berkley_314/drew_storage/enrolled_video_folders/stills --cuda_visible 0


ap = argparse.ArgumentParser()
ap.add_argument("--to_process", required = True)
ap.add_argument("--dest", required = True)
ap.add_argument("--batch_size", required = True)
ap.add_argument("--stills", required = True) #stills should be on the same hard drive as dest. i should make this automatically created...
ap.add_argument("--cuda_visible", required = True)
args = vars(ap.parse_args())

to_process_dir = args['to_process']
dest = args['dest'] #e.g. "Grouper Moon/Grouper Moon Image Dataset Project/undistributed video"
cuda_v = args['cuda_visible']
stills = args['stills']
bs = args['batch_size']
first_os_walk = next(os.walk(to_process_dir))
root = first_os_walk[0]
subdirs = first_os_walk[1]
ts = int(time.time())

#e_fn = "enroll_" + str(ts) + ".sh"
p_fn = "process_" + str(ts) + ".sh"
#e_fn = os.path.join('scripts_batch_process',e_fn)
p_fn = os.path.join('scripts_batch_process',p_fn)

# with open(e_fn, "w+") as e_f:
#     for d in subdirs:
#         fullpath = root + '/' + d
#         e_l = "./external_enroll_video_folder.sh --dir  " + '\"' + fullpath + '\"' + " --enroll " + '\"' + dest + '\"'
#         e_f.write(e_l)
#         e_f.write("\n")

# with open(p_fn, "w+") as p_f:
#     for d in subdirs:
#         fullpath = root + '/' + d
#         p_l = "./external_process_video_folder.sh --dir  " + '\"' + fullpath + '\"' + " --enroll " + '\"' + dest + '\"' + " --stills " + '\"' + stills + '\"' +  " --period 0.25 --batch_size " + bs + " --cuda_visible " + cuda_v
#         p_f.write(p_l)
#         p_f.write("\n")

        
with open(p_fn, "w+") as p_f:
    for d in subdirs:
        fullpath = root + '/' + d
        e_l = "./util/external_enroll_video_folder.sh --dir  " + '\"' + fullpath + '\"' + " --enroll " + '\"' + dest + '\"' + ' &&'
        p_f.write(e_l)
        p_f.write("\n")
        
    for i, d in enumerate(subdirs):
        fullpath = root + '/' + d
        p_l = "./util/external_process_video_folder.sh --dir  " + '\"' + fullpath + '\"' + " --enroll " + '\"' + dest + '\"' + " --stills " + '\"' + stills + '\"' +  " --period 0.25 --batch_size " + bs + " --cuda_visible " + cuda_v
        if i != len(subdirs) - 1: p_l = p_l + ' &&' 
        p_f.write(p_l)
        p_f.write("\n")
        
