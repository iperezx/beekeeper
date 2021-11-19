#!/usr/bin/env python3

import requests
import dateutil.parser
import datetime
import sys
import time
import os


BEEKEEPER_URL = os.getenv("BEEKEEPER_URL", "http://localhost:5000")


# example input 2021-11-19T02:07:22
# returns datetime.datetime
def parseTime(timestamp):
    #dateutil.parser.isoparse('2008-09-03T20:56:35.450686')
    return dateutil.parser.isoparse(timestamp)

def get_candidates():

    if BEEKEEPER_URL == "":
        print(f"BEEKEEPER_URL not defined")
        sys.exit(1)

    print(f"BEEKEEPER_URL: {BEEKEEPER_URL}")
    url = f'{BEEKEEPER_URL}/state'
    print(f"url: {url}")

    try:
        resp  = requests.get(url)
    except Exception as e:
        raise Exception(f"GET request to {url} failed: {str(e)}")


    if resp.status_code != 200:
        raise Exception(f"status_code: {resp.status_code} body: {resp.text}")

    nodes = resp.json()


    candidates=[]

    if not "data" in nodes:
        raise Exception("Field data missing")

    for n in nodes['data']:
        node_id  = n["id"]
        #print("id: "+node_id)
        #print("wes_deploy_event: "+n["wes_deploy_event"])
        if n.get("beehive") in ["", None]:
            print(f"node {node_id} does not belong to a beehive")
            continue

        if n.get("wes_deploy_event") in ["", None]:
            print(f"scheduling node {node_id} for wes deployment (reason: no previous deployment)")
            candidates.append(n)
            continue

        ts = parseTime(n["wes_deploy_event"])

        ts_diff = datetime.datetime.utcnow() - ts
        if ts_diff.days >= 60: #???? check with others
            print(f"scheduling node {node_id} for wes deployment (reason: no recent deployment)")
            candidates.append(n)
            continue

        print(f"node {node_id} needs no deployment")

    return candidates


def try_wes_deployment(candidates):


    success_count = 0

    for n in candidates:
        node_id  = n["id"]
        #curl localhost:5000/node/0000000000000001 -d '{"deploy_wes": true}'
        d_url = f"{BEEKEEPER_URL}/node/{node_id}"
        resp = requests.post(d_url, json={"deploy_wes":True})
        if resp.status_code != 200:
            print(d_url)
            print(f"Something went wrong: status_code: {resp.status_code} body: {resp.text}")
        result = resp.json()
        if not "success" in result:
            print(d_url)
            print(f"Something went wrong: status_code: {resp.status_code} body: {resp.text}")
        if not result["success"]:
            print(d_url)
            print(f"Something went wrong: status_code: {resp.status_code} body: {resp.text}")

        success_count += 1
        time.sleep(2)

    print(f"{success_count} out of {len(candidates)} successful.")
    print("done")

    return


while True:

    candidates = []
    try:
        candidates = get_candidates()
    except Exception as e:
        print(f"error: get_candidates returned: {str(e)}")

    if len(candidates) == 0:
        print("no candidates for wes deployment found")
    else:
        print("candidates:")
        print(candidates)
        try_wes_deployment(candidates)

    print("waiting 5 minutes...")
    time.sleep(5*60)


