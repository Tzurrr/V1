import redis
import os
import requests
import dot_finder
import elogger


def send(filepath):
    r = redis.Redis()
    dot = dot_finder.find(filepath)
    get_val = r.get(f"{filepath[:dot - 2]}")
#    print(1, get_val)
    arr = [("files", open(filepath, "rb")), ("files", open(get_val, "rb"))]
    os.remove(get_val)
    os.remove(filepath)
    resp = requests.post(url="http://127.0.0.1:80/", files=arr)
 #   print(resp.json)
    if str(resp.json) == "<bound method Response.json of <Response [200]>>":
  #      print("passed")
        elogger.write("sent")
    else:
        elogger.write("didntsent")
   #     print("failed")
