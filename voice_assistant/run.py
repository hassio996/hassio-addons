#!/usr/bin/env python3

import json, atexit, time, wave, io, subprocess
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from threading import Thread
from runner import PreciseEngine, TriggerDetector

def get_input_stream( name ):
  if(name=="local_default"):
    import pyaudio
    pa = pyaudio.PyAudio()
    stream = pa.open(16000, 1, pyaudio.paInt16, True, frames_per_buffer=CHUCK_SIZE)
  if getattr(stream.read, '__func__', None) is pyaudio.Stream.read:
    stream.read = lambda x: pyaudio.Stream.read(stream, x // 2, False)
  return stream

def get_func( func_str ):
  import_file = func_str.rsplit('.',1)[0]
  try:
    exec("import " + import_file)
    return eval(func_str)
  except Exception as e:
    print("Can't import", func_str, "----", e)
    return None
  
def get_wav_data( raw_data ):
        # generate the WAV file contents
        with io.BytesIO() as wav_file:
            with wave.open(wav_file, "wb") as wav_writer:
                wav_writer.setframerate(16000)
                wav_writer.setsampwidth(2)
                wav_writer.setnchannels(1)
                wav_writer.writeframes(raw_data)
                wav_data = wav_file.getvalue()
                wav_writer.close()
        return wav_data

def get_flac_data( wav_data ):

  process = subprocess.Popen(["/usr/bin/flac",
                              "--stdout", "--totally-silent",
                              "--best",
                              "-",
                              ],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, startupinfo=None)
  flac_data, stderr = process.communicate(wav_data)
  return flac_data

def recognize_google_cn(flac_data, language="zh-CN", pfilter=0, show_all=False):

        key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
        url = "http://www.google.cn/speech-api/v2/recognize?{}".format(urlencode({
                  "client": "chromium",
                  "lang": language,
                  "key": key,
                  "pFilter": pfilter
                  }))
        request = Request(url, data=flac_data, headers={"Content-Type": "audio/x-flac; rate=16000"})

        # obtain audio transcription results
        try:
            response = urlopen(request)
        except HTTPError as e:
            print("recognition request failed: {}".format(e.reason),flush=True)
        except URLError as e:
            print("recognition connection failed: {}".format(e.reason),flush=True)
        response_text = response.read().decode("utf-8")

        # ignore any blank blocks
        actual_result = []
        for line in response_text.split("\n"):
            if not line: continue
            result = json.loads(line)["result"]
            if len(result) != 0:
                actual_result = result[0]
                break

        # return results
        if show_all: return actual_result
        if not isinstance(actual_result, dict) or len(actual_result.get("alternative", [])) == 0:
            print("recognition result error",flush=True)
            return ""

        if "confidence" in actual_result["alternative"]:
            # return alternative with highest confidence score
            best_hypothesis = max(actual_result["alternative"], key=lambda alternative: alternative["confidence"])
        else:
            # when there is no confidence available, we arbitrarily choose the first hypothesis.
            best_hypothesis = actual_result["alternative"][0]
        if "transcript" not in best_hypothesis:
            print("recognition result format error",flush=True)
            return ""
        return best_hypothesis["transcript"]


def handle_predictions( va ):
  """Continuously check Precise process output"""
  input_device = va["input_device"]
  output_entity_id = va["output_entity_id"]
  model_file = va["model_file"]
  threshold = va["threshold"]
  show_match_level_realtime = va["show_match_level_realtime"]
  op_waken = va["op_waken"]
  op_recvd = va["op_recvd"]
  op_react = va["op_react"]
  tts_service = va["tts_service"]
  matches[input_device] = []

  stream_in = get_input_stream(input_device)
  detector = TriggerDetector(CHUCK_SIZE, 1.0-threshold)
  engine = PreciseEngine('/precise-engine/precise-engine',
                         model_file,
                         chunk_size = CHUCK_SIZE)
  func_waken = get_func( op_waken )
  func_recvd = get_func( op_recvd )
  func_react = get_func( op_react )
  engine.start()

  while True:
    chunk = stream_in.read(CHUCK_SIZE)
    prob = engine.get_prediction(chunk)
    if show_match_level_realtime:
      matches[input_device].append(prob)
    if detector.update(prob):
      func_waken(tts_service, output_entity_id)
      audio = stream_in.read(CHUCK_SIZE*CHUCKS_TO_READ)
      func_recvd(tts_service, output_entity_id)
      wav_data = get_wav_data( audio )
      flac_data = get_flac_data(wav_data)
      speech_in = recognize_google_cn(flac_data)
      func_react(speech_in, tts_service, output_entity_id)



CHUCK_SIZE = 2048
CHUCKS_TO_READ = int(5*2*16000/2048)

CONFIG_PATH = "/data/options.json"
with open(CONFIG_PATH) as fp:
  config = json.load(fp)

matches = {}
for va in config["voice_assistant"]:
  thread = Thread(target=handle_predictions,
                  args=(va,),
                  daemon=True)
  thread.start()


while(True):
    time.sleep(1)
    for key in matches:
      if(len(matches[key])>0):
        max_match = max(matches[key])
        matches[key].clear()
        print('the match level of %s: %.2f' % (key, max_match), flush=True)
