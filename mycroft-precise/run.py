#!/usr/bin/env python3

import os
import json
import time
from requests import post
from runner import PreciseEngine, PreciseRunner

CONFIG_PATH = "/data/options.json"
with open(CONFIG_PATH) as fp:
  config = json.load(fp)

options = config['models']

matches = {}
def on_prediction(show, model, prob):
    if show:
        matches[model].append(prob)

headers = {
    "Authorization": "Bearer " + os.getenv('SUPERVISOR_TOKEN'),
    "content-type": "application/json",
}

for option in options:
    url = "http://supervisor/core/api/events/" + option["event_type"]
    matches[option["model_file"]]=[]
    engine = PreciseEngine('/precise-engine/precise-engine',
                           option["model_file"])
    runner = PreciseRunner(engine,
                           on_activation=eval("lambda: post('%s', headers=headers)"%(url)),
                           on_prediction=eval("lambda x: on_prediction(%s, '%s', x)"%(option["show_match_level_realtime"],option["model_file"])),
                           sensitivity = 1.0-option["threshold"]
                           )
    runner.start()

while(True):
    time.sleep(1)
    for m in matches:
      if(len(matches[m])>0):
        max_match = max(matches[m])
        matches[m].clear()
        print('the match level of %s: %.2f' % (m, max_match), flush=True)
