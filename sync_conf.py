import shutil
import os
import urllib2
import json
import urllib
import stat

import role_conf

role = role_conf.role

def sync_conf():
    if not role.strip():
        print "role not setted"
        return False
    conf_path = "./conf"
    if os.path.exists(conf_path):
        shutil.rmtree(conf_path,ignore_errors=True)
    os.mkdir(conf_path)
    folders,files,ip = get_remote_conf_info()
    if (not folders and not files) or not ip:
        print "failed to get remote configure info"
        return False
    try:
        # setup folder
        for folder in folders:
            foler_path = os.path.join(conf_path,folder)
            os.makedirs(foler_path)
        for file_info in files:
            file,executable = file_info["filepath"],file_info["executable"]
            content = download(file,ip)
            if not content:
                return False
            full_relatve_filepath = os.path.join(conf_path,file)
            with open(full_relatve_filepath,"w") as fd:
                fd.write(content)
            if executable:
                old_mode = os.stat(full_relatve_filepath).st_mode
                os.chmod(full_relatve_filepath,old_mode|stat.S_IXUSR)
        checkdir()
        return True
    except Exception,e:
        print str(e)
        return False

def get_remote_conf_info():
    url = "http://conf.cloutropy.com:12000/filelist?role=%s" % role
    try:
        content = urllib2.urlopen(url).read()
        result = json.loads(content)
        if result.get("result") == "fail":
            print content
            return None,None,None
        return result.get("folders"),result.get("files"),result.get("ip")
    except Exception,e:
        print str(e)
        return None,None,None

def download(filepath,ip):
    args = {"role":role,"ip":ip,"filepath":filepath}
    args = urllib.urlencode(args)
    url = "http://conf.cloutropy.com:12000/download?%s" % args
    try:
        content = urllib2.urlopen(url).read()
        return content
    except Exception,e:
        print str(e)
        return None

def checkdir():
    conf_path = "./conf/flume-conf.properties"
    with open(conf_path,'r') as conf:
        lines = conf.readlines()
    for line in lines:
        if line.find('topic_counter_file') >= 0 or line.find('progress_file_path') >= 0:
            file =  line.split('=')[1].replace('\n','')
            if os.system('mkdir -p $(dirname '+file+')') != 0:
                print 'check the topic_counter_file and progress_file_path confs'

if __name__ == "__main__":
    sync_conf()
