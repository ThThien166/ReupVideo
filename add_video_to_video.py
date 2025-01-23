import subprocess
import os
import cv2
import random
# import play

ffprobe_path = os.path.join(os.path.dirname(__file__), 'ffmpeg/ffprobe.exe')
ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg/ffmpeg.exe')


def get_video_duration(file_path):
    result = subprocess.run([ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)


def get_video_size(video_path):
    command_main = [ffprobe_path, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of',
               'csv=s=x:p=0', video_path]
    result = subprocess.run(command_main, capture_output=True, text=True)
    output = result.stdout.strip()
    width, height = output.split('x')
    return int(width), int(height)


def resize_video_main(video_path_main,video_path_bgr,out_video_rezise, re_wi, re_he):
    
    width_b,height_b =get_video_size(video_path_bgr)
    width_mre = width_b - re_wi*width_b
    height_mre = height_b - re_he*width_b
    
        
            
    ffmpeg_cmd = [ffmpeg_path,
        '-i', video_path_main, '-vf', f'scale={width_mre}:{height_mre}', '-c:a', 'copy', out_video_rezise
    ]
    subprocess.run(ffmpeg_cmd)
    return out_video_rezise

def cut_add_time_video(video_path_bgr, out_video_rezise, out_video_time_bgr):
    dura_bgr = get_video_duration(video_path_bgr)
    dura_main = get_video_duration(out_video_rezise)
    
    if dura_bgr > dura_main:
        start_time = 0
        end_time = dura_main
        ffmpeg_cmd = [
        ffmpeg_path,
        '-i', video_path_bgr,
        '-ss', str(start_time),
        '-to', str(end_time),
        '-c', 'copy',
        out_video_time_bgr
        ]
        subprocess.run(ffmpeg_cmd)
    elif dura_bgr <= dura_main:
        factor = dura_main/dura_bgr
        ffmpeg_cmd2 = [
        ffmpeg_path,
        '-i',
        video_path_bgr,
        '-filter:v',
        f'setpts={factor}*PTS',
        '-c:a',
        'copy',
        out_video_time_bgr
        ]
        subprocess.run(ffmpeg_cmd2)

    return out_video_time_bgr

def add_video_to_video(out_video_rezise, out_video_time_bgr, output_path, time_blend):
    ffmpeg_cmd = [
    ffmpeg_path,
    "-i", out_video_time_bgr,
    "-i", out_video_rezise,
    "-filter_complex", f"[1:v]format=argb,fade=t=in:st=0:d={time_blend}:alpha=1,fade=t=out:st=99999999:d=1:alpha=1[int];[0:v][int]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[out]",
    "-map", "[out]",
    "-map", "1:a:0", 
    "-c:a", "copy","-y",
    output_path
    ]
    subprocess.run(ffmpeg_cmd)
    os.remove(out_video_rezise)
    os.remove(out_video_time_bgr)


output_path = os.path.join(os.path.dirname(__file__), 'output_video_INVIDEO.mp4')
video_path_bgr = os.path.join(os.path.dirname(__file__), 'video2.mp4')
video_path_main = os.path.join(os.path.dirname(__file__), 'videoSD.mp4')
out_video_rezise=os.path.join(os.path.dirname(__file__),'temp/'+str(random.randint(1, 100000))+'.mp4')
out_video_time_bgr=os.path.join(os.path.dirname(__file__),'temp/'+str(random.randint(100001, 200000))+'.mp4')

out_video_rezise = resize_video_main(video_path_main,video_path_bgr,out_video_rezise, re_wi=0.1, re_he=0.1)
out_video_time_bgr = cut_add_time_video(video_path_bgr, out_video_rezise, out_video_time_bgr)
add_video_to_video(out_video_rezise, out_video_time_bgr, output_path, time_blend=2)
# play.play_video(output_path)
