#!/bin/bash

#source of file https://gist.github.com/russfeld/0878b1f8eaf7409136b9125ce5e1458f

# =================================================================
# Stream configuration file for Raspberry Pi Camera
#
# @author Russell Feldhausen (russfeldh@gmail.com)
# @version 2019-06-05
#
# This set of commands should allow you to stream video from your 
# Raspberry Pi Camera to Twitch and Youtube (and possibly other
# RTMP endpoints) with decent quality and performance.
#
# You may need to install raspivid and/or ffmpeg to use this script.
# 
# This was tested and built on Raspbian 9 installed using Noobs
# =================================================================


# Set width and height of output video
WIDTH=1920
# WIDTH=1280
HEIGHT=1080
# HEIGHT=720

# Set output framerate
FRAMERATE=30

# Set keyframe spacing (must be double the framerate)
KEYFRAME=60

# Set bitrate (Twitch recommends 3500000)
BITRATE=3000000

# Set video offset
# OFFSET=0.5
OFFSET=1.1

# Set Audio input (check using "arecord -l")
INPUT=plughw:CameraB409241,0


#TODO multistreaming maybe to yt as well someday?
# Set stream URL -> will use frankfurt ingest
URL=rtmp://live-fra02.twitch.tv/app/

# Set stream key
KEY=$1

# Command
# other version adapted from og but under 30fps sometimes
# raspivid -n -t 0 -w $WIDTH -h $HEIGHT -fps $FRAMERATE -b $BITRATE -g $KEYFRAME -o - | ffmpeg -use_wallclock_as_timestamps 1 \
#     -f h264 -thread_queue_size 10240 -r $FRAMERATE -i - -g $KEYFRAME -itsoffset $OFFSET \
#     -f alsa -thread_queue_size 10240 -ac 2 -i $INPUT -strict experimental -threads 4 \
#     -vcodec copy -acodec aac -ac 2 -ar 44100 -ab 128k -b:v $BITRATE -preset ultrafast -f flv "${URL}/${KEY}"

# combined mic version with some tweaks from og and so on
# no stdin and loglevel error are VERY important in ensuring possiblity and stability in bg process not filling up buffer from https://stackoverflow.com/a/47114881 and not suspending because of missing tty in
# this versio has no status output and no dynamic input and reconnect arguments to be best in bg tasks of python service
raspivid -n -o - -t 0 -w $WIDTH -h $HEIGHT -fps $FRAMERATE -b $BITRATE -g $KEYFRAME | ffmpeg -use_wallclock_as_timestamps 1 \
    -nostdin -loglevel error \
    -thread_queue_size 20480 -f h264 -r 30 -i - \
    -f alsa -thread_queue_size 20480 -ac 2 -itsoffset $OFFSET -i $INPUT -strict experimental -threads 4 \
    -vcodec copy -acodec aac -ac 2 -ar 44100 -ab 128k -f flv "${URL}/${KEY}" \
    -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 15  # don_t break connection on spotty internet but keep and reconnect

# =================================================================
# Full Documentation of Command Options
# 
# +++ raspivid +++
# -n = no preview window
# -t = time to capture (0 to disable, which allows streaming)
# -w = video width
# -h = video height
# -fps = output framerate (max 30 for 1080p, 60 for 720p)
# -b = bitrate
# -g = keyframe rate (refresh period)
# -o - = output to stdout (allows piping to ffmpeg)
#
# +++ ffmpeg +++
# -f lavfi = use lavfi filter (see note below)
# -i anullsrc = grab blank input (see note below)
# -c:a aac = set audio codec to aac
# -r = output framerate (should match raspivid framerate)
# -i - = read input from stdin (piped from ffmpeg)
# -g = keyframe rate (refresh period)
# -strict experimental = allow nonstandard things
# -threads 4 = set number of encoding threads to 4 (# of cores)
# -vcodec copy = use video as-is (do not re-encode video)
# -map 0:a = use the audio from input 0 (see note below)
# -map 1:v = use the video from input 1 (raspivid)
# -b:v = bitrate
# -preset ultrafast = use the ultrafast encoding preset
# -f flv = set output format to flv for streaming
# "${URL}/{KEY}" = specify RTMP URL as output for stream
#
# ** NOTE **
# According to some information online, YouTube will reject a live
# stream without an audio channel. So, in the ffmpeg command above
# a blank audio channel is included. It was not required for Twitch
# in my testing. 
# =================================================================

