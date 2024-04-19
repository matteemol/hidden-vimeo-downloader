#!/usr/bin/python3
import requests
import json
import os
import shutil
import sys

master = "https://65vod-adaptive.akamaized.net/exp=1711276332~acl=%2F12168687-ca09-487d-99b7-fbc1037fa8b8%2F%2A~hmac=dc5d2e823e9e72fb26167cfd62eb773e4ca5bb1ac351363218b1ca0d94e71901/12168687-ca09-487d-99b7-fbc1037fa8b8/sep/video/35d445b9,4652c052,5ea4bda4,e5fe3650,ec3db5ec/audio/b29e1245,d1d94b51,e6a153b8/master.json"
# ffmpeg -i 35d445b9_final_video.mp4 -i 35d445b9_final_audio.mp4 -c copy 12168687-ca09-487d-99b7-fbc1037fa8b8final_video.mp4
if len(sys.argv) != 2:
    print("Wrong number of arguments")
    print("python3 vimeo-downloader.py <url of master.json>")
    exit()

master_json_url = sys.argv[1]
print(master_json_url)


def parse_json(json_text):
    global clip_id, audio_id, video_id, number_of_segments, segment_base_name, segment_base_ext
    json_data = json.loads(json_text)
    clip_id = json_data["clip_id"]
    video_id = json_data["video"][0]["id"]
    audio_id = json_data["video"][0]["id"]
    number_of_segments = len(json_data["video"][0]["segments"])
    segment_base_name, segment_base_ext = json_data["video"][0]["segments"][0]["url"].split("1")


base_url = master_json_url.split("video/")[0]
print(base_url)
clip_id = ""
audio_id = ""
video_id = ""
number_of_segments = ""
segment_base_name = ""
segment_base_ext = ""


#headers = {'content-type': 'text/plain;charset=UTF-8',
#           'cookie': 'vuid=pl433710374.638549744; language=en; has_logged_in=1; is_logged_in=1; player="volume=0.437"; _ga=GA1.2.1010891273.1690640619; _cfuvid=lU8NQzVR1grxLEXFjMY_5RyjmL9dPPF8ZaSMmlHN2zk-1711324419801-0.0.1.1-604800000; __cf_bm=sVibAfh5VkC7he0lkXhuxyWNOLx0Frkk5MIUHdG3vJ4-1711348804-1.0.1.1-B0uRXJ2OhBEa2Tjrf_.bXkkvbeW36kh_gOp4Ql5gfa.jjr9ha94G0HJcBofEcvEtlqo6GA.i4QU3e_klzkQBUA'}

r = requests.get(master_json_url)#, headers=headers)

parse_json(r.text)

out_video = "segments_video_" + clip_id
out_audio = "segments_audio_" + clip_id
try:
    shutil.rmtree(out_video)
    shutil.rmtree(out_audio)
except:
    pass

if not os.path.exists(out_video):
    os.mkdir(out_video)
if not os.path.exists(out_audio):
    os.mkdir(out_audio)

print("Clip_ID: " + str(clip_id))
print("Video_ID: " + str(video_id))
print("Audio_ID: " + str(audio_id))
print("Number of Segments: " + str(number_of_segments) )
print()
print("Start Download")
full_video = b""
full_audio = b""
for i in range(0, number_of_segments+1):
    # video
    current_segement_url = base_url + "video/" + str(video_id) + "/chop/" + segment_base_name + str(i) + segment_base_ext
    r = requests.get(current_segement_url)
#    v_seg_file = os.path.normpath(os.path.join(out_video ,"video-" + segment_base_name + str(i) + segment_base_ext))
    v_seg_file = os.path.join(out_video ,"video-" + segment_base_name + str(i) + segment_base_ext)

#    v_seg_file = v_seg_file.split("\\")[0] + "\\" + v_seg_file.split("\\")[1]
#    v_seg_file.encode('unicode-escape')
    print(v_seg_file)
#    exit()
    with open(v_seg_file, "wb") as f:
        f.write(r.content)
    full_video += r.content

    # audio
    current_segement_url = base_url + "audio/" + str(video_id) + "/chop/" + segment_base_name + str(i) + segment_base_ext
    r = requests.get(current_segement_url)
    a_seg_file = os.path.normpath(os.path.join(out_audio ,"audio-" + segment_base_name + str(i) + segment_base_ext))
    a_seg_file = a_seg_file.split("\\")[0] + "\\" + a_seg_file.split("\\")[1]
    with open(a_seg_file, "wb") as f:
        f.write(r.content)
    full_audio += r.content

#    if i % 10 == 0:
#        print(str(i) + "/" + str(number_of_segments) + " downloaded")
    print(str(i) + "/" + str(number_of_segments) + " downloaded")

with open(video_id + "_final_video.mp4", "wb") as f:
    f.write(full_video)

with open(video_id + "_final_audio.mp4", "wb") as f:
    f.write(full_audio)

print("Merge the output files with the following command:")
print("$ ffmpeg -i " + video_id + "_final_video.mp4" + " -i " + video_id + "_final_audio.mp4" + " -c copy " + clip_id + "final_video.mp4")