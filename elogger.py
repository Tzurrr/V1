import json
import logging
import ecs_logging
import requests
import uuid
import os

def write(event_string):
    #print("-a")
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('elvis.json')
    handler.setFormatter(ecs_logging.StdlibFormatter())
    logger.addHandler(handler)
    json_UUID = uuid.uuid4()
    #print("a")
    keywords_arr = ["arrivedtoserver", "sent", "didntsent", "wrote"]
    
    # TODO: add value check

    #print("f")
    logger.info(event_string, extra={"http.request.method": "get", "UUID": json_UUID})
    #print("g")
    a_file = open("/home/tzur/elvis.json", "r")
    #print("h")
    a_json = json.load(a_file)
    #print("i")
    a_file.close()

    os.remove("/home/tzur/elvis.json")

    doc_UUID = uuid.uuid4()
    #print("j")
    resp = requests.put(url=f"http://13.81.211.207:9200/{event_string}/_doc/{doc_UUID}", json=a_json,
                        headers={'Content-Type': 'application/json'})
    print(resp.json())
