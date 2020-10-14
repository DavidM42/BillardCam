#!/bin/bash

# got from comment https://gist.github.com/russfeld/0878b1f8eaf7409136b9125ce5e1458f#gistcomment-3455573

#TODO input url and key from some variable to load in to push this to git someday

# Set width and height of output video
WIDTH=1920
HEIGHT=1080

# Set output framerate
FRAMERATE=30

#Set Rotation
ROTATION=0

# Set keyframe spacing (must be double the framerate)
KEYFRAME=60

# Set bitrate (Twitch recommends 3500000)
BITRATE=3500000

# Camera Settings (includes commands)
SATURATION=25         #sa
SHARPNESS=            #sh
CONTRAST=            #co
BRIGHTNESS=           #br
AWB=               #awb
ISO=                  #iso
SHUTTERSPEED=         #ss
EXPOSURE=             #ex
EV=0                #ev
ANTIFLICKER=          #fli
IMAGEEFFECT=          #ifx

# Set video offset
OFFSET=0.5

# Set Audio input (check using "arecord -l")
INPUT=plughw:0,0

# Set stream URL -> will use frankfurt ingest
URL=rtmp://live-fra02.twitch.tv/app/

# Set stream key
KEY=$1


# Command
raspivid -o - -t 0 -w $WIDTH -h $HEIGHT -fps $FRAMERATE -b $BITRATE -rot $ROTATION -g $KEYFRAME -sa $SATURATION -awb $AWB -ev $EV -f | /home/pi/ffmpeg/ffmpeg -use_wallclock_as_timestamps 1 -thread_queue_size 10240 -f h264 -r 30 -i - -itsoffset $OFFSET -f alsa -thread_queue_size 10240 -ac 2 -i $INPUT -vcodec copy -acodec aac -ac 2 -ar 44100 -ab 192k -f flv "${URL}/${KEY}"

