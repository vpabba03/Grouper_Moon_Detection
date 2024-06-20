import argparse
import os
import time 

ap = argparse.ArgumentParser()
ap.add_argument("--to_download", required = True) #a .txt file of directories, starting with My Drive/ 
ap.add_argument("--dest", required = True)
args = vars(ap.parse_args())

to_dl_file = args['to_download']
dest = args['dest'] #e.g. "Grouper Moon/Grouper Moon Image Dataset Project/undistributed video"
#import pdb; pdb.set_trace()
ts = int(time.time())

fn = "download_" + str(ts) + ".sh"
fn = os.path.join('scripts_batch_downloads',fn)

with open(fn, "w+") as f:
    with open(to_dl_file, "r") as dl:
        for d in dl:
            d = d.replace("My Drive/", "labdrive:")
            d = d.rstrip("\n")
            l = "./util/labdrive_dl.sh --src " + '\"' + d + '\"' + " --dest " + '\"' + dest + '\"'
            f.write(l)
            f.write("\n")