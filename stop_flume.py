import json
import urllib2
import time
import os
import posixfile

host = "127.0.0.1"

def close_flume():
    url = "http://%s:11000/close" % host
    try:
        resp = urllib2.urlopen(url)
        return True
    except Exception,e:
        return False

def get_progress():
    url = "http://%s:11000/metrics" % host
    progress = {}
    try:
        resp = urllib2.urlopen(url)
        content = resp.read()
        result = json.loads(content)
        for i in range(1,11):
            channel_name = "CHANNEL.ch%d" % i
            channel_attr = result.get(channel_name)
            if channel_attr and channel_attr.has_key("ChannelSize"):
                channel_size = channel_attr["ChannelSize"]
                progress["ch%d"%i] = int(channel_size)
        return progress
    except Exception,e:
        return None

def wait():
    pid_file = "./flume.pid"
    if not os.path.exists(pid_file):
        return
    fd = posixfile.open(pid_file)
    fd.lock("r|")
    fd.lock("u")


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

def killProcess():
    try:
        pid = open("./flume.pid","r").read().strip()
        pid = int(pid)
        import signal
        os.kill(pid,signal.SIGTERM)
    except Exception,e:
        print str(e)
        return False

def main():
    if not testAlive():
        print "the process is already closed"
    if not close_flume():
        print "the http interface to the flume is closed"
    else:
        while True:
            progress_list = get_progress()
            if not progress_list:
                break
            empty = True
            for channel_name,progress in progress_list.iteritems():
                print "%s-channel_size: %d" % (channel_name,progress)
                if progress != 0:
                    empty = False
            print "---------------------------------------\n"
            if empty:
                # send signal to the process
                killProcess()
                break
            time.sleep(2)
    # waiting for the process to quit
    wait()
    print "the program is to closed"

if __name__ == "__main__":
    main()