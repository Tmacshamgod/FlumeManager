import os
import posixfile

import sync_conf

def testAlive():
    pid_file = "./flume.pid"
    if not os.path.exists(pid_file):
        return False
    try:
        fd = posixfile.open(pid_file)
        fd.lock("r")
        fd.lock("u")
        return False
    except IOError,e:
        return True

if __name__ == "__main__":
    if testAlive():
        print "Another instance is already running ... ",
    else:
        # sync the configure
        if not sync_conf.sync_conf():
            print "Failed to sync configure from remote ConfigureServer"
        else:
            cmd_line = "nohup bin/flume-ng agent --conf conf -f conf/flume-conf.properties --name agent -Dflume.monitoring.type=http -Dflume.monitoring.port=11000 > /dev/null &"
            os.system(cmd_line)
