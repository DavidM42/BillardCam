NOT possible on pi because of hardware -> would need some codec not copy
so something like libx264 which is too much for cpu
option of gpu accel encoding could be explored
https://www.reddit.com/r/raspberry_pi/comments/5677qw/hardware_accelerated_x264_encoding_with_ffmpeg/

could so something like this to remove fisheye effect
see https://stackoverflow.com/a/40659507 and 
https://www.danielplayfaircal.com/blogging/ffmpeg/lensfun/v360/lenscorrection/fisheye/dodgeball/2020/03/24/correcting-lens-distortion-with-ffmpeg.html
for more info
`-vf "lenscorrection=cx=0.5:cy=0.5:k1=-0.130:k2=-0.020"`