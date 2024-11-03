#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from colorama import Fore, Back, Style
from collections import deque
from itertools import islice
from mutagen.mp4 import MP4, MP4Cover
from datetime import datetime
from PIL import Image
from io import BytesIO

import subprocess
import ffmpeg
import random
import sys
import os
import shutil
import librosa

AUDIO_FILE_EXTENSIONS = (".mp3", ".m4a", ".ogg", ".flac", ".wav", ".opus")
IMAGE_FILE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")

# setup encoders
if sys.platform == "darwin":
  AUDIO_ENC = "aac_at"
  VIDEO_ENC = "hevc_videotoolbox"
else:
  AUDIO_ENC = "aac"
  VIDEO_ENC = "libx264"

# https://stackoverflow.com/questions/75813482/generate-random-numbers-in-a-range-while-keeping-a-minimum-distance-between-valu
def gap_random_uniform(low, high, gap):
    slots, freespace = deque([(low, high)]), high - low
    while slots:
        x = random.uniform(0, freespace)
        while True:
            slotlow, slothigh = slots[0]
            slotspace = slothigh - slotlow
            if x < slotspace:
                slots.popleft()
                freespace -= slotspace
                xlow, xhigh = x - gap, x + gap
                if xlow > 0:
                    slots.append((slotlow, slotlow + xlow))
                    freespace += xlow
                if xhigh < slotspace:
                    slots.appendleft((slotlow + xhigh, slothigh))
                    freespace += slotspace - xhigh
                yield x + slotlow
                break
            x -= slotspace
            slots.rotate(-1)


def get_audio_files() -> list[str]:
  """gets all audio files the user added"""
  files = os.listdir("sounds")
  files = [os.path.join("sounds", f) for f in files if f.endswith(AUDIO_FILE_EXTENSIONS)]
  return files

def transcode_to_opus(file: str) -> str:
  """transcodes the file to opus then returns the path"""
  outfile = os.path.join(".tmp", f"{os.path.basename(file)}.opus")
  stream = ffmpeg.input(file)
  stream = stream.output(outfile, acodec="libopus", audio_bitrate=160_000)
  stream.run(quiet=True)
  return outfile

def generate_silence(dur: float) -> str:
  filename = os.path.join(".tmp", f"silence_{dur}.ogg")
  stream = ffmpeg.input("anullsrc=channel_layout=stereo:sample_rate=48000", t=dur, f="lavfi")
  #stream = ffmpeg.filter("aevalsrc", 0)
  stream = stream.output(filename, acodec="libopus", audio_bitrate=160_000)
  stream.run(quiet=True)
  return filename


def main() -> None:
  """Main program code"""

  print(f"{Style.BRIGHT}{Back.BLUE}{Fore.WHITE}     BrokenSilence     {Style.RESET_ALL}")
  print(f"{Style.DIM}{Fore.CYAN}This program will walk you through generating a \"1 hour of silence occasionally broken up\nby <sound>\" video so you can annoy your friends with never heard before sounds :)")
  print(Style.RESET_ALL)
  print(f"{Style.BRIGHT}{Fore.GREEN}How to use:{Style.RESET_ALL}")
  print(f"{Fore.GREEN}1. Put all your desired sounds into the `sounds/` folder{Style.DIM}")
  print(f"   | This script will see the following filetypes: {', '.join(AUDIO_FILE_EXTENSIONS)}")
  print(f"   | They will be converted to opus 160k internally.")
  print(f"2. Place the image you would like to use for the cover art and video into the `images` directory.{Style.DIM}")
  print(f"   | You will then be prompted to select an image in the folder and the script will generate")
  print(f"   | a video and audio track for you! Make sure your image has one of the following file extensions:")
  print(f"   | {', '.join(IMAGE_FILE_EXTENSIONS)}")
  print(f"{Style.NORMAL}3. Let the script guide you through the process.")
  print(f"4. Select you preferred export format.")
  print(f"5. Share your video for maximum annoyance!")
  print(f"{Style.DIM}   | If you upload to video sharing sites, please share a link to the repository")
  print(f"   | so others can find this project too!")
  print(Style.RESET_ALL)

  input(f"{Style.DIM}Press Enter to continue...{Style.RESET_ALL}")

  if os.path.exists(".tmp"):
    shutil.rmtree(".tmp")
  os.mkdir(".tmp")
  
  audio_files = get_audio_files()
  if len(audio_files) == 0:
    print(f"{Fore.RED}==>  ERR: No audio files found")
    exit(1)

  print(f"\n{Style.BRIGHT}Found the following audio files:{Style.RESET_ALL}{Style.DIM}")
  for file in audio_files:
    print("  - " + file)
  input(f"\n{Style.DIM}Press Enter to continue...{Style.RESET_ALL}")
  print()

  processed_files = []
  durations = []

  images = [os.path.join("images", img) for img in os.listdir("images")]

  print(f"{Style.BRIGHT}Found the following images files:{Style.RESET_ALL}{Style.DIM}\n")

  for i, img_path in enumerate(images):
    print(f"  {i+1: 2}) {img_path}")
  print()

  img_num = int(input(f"{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}Select image from list: {Style.RESET_ALL}"))
  print()

  img = images[img_num-1]

  for file in audio_files:
    print(f"{Fore.BLUE}{Style.DIM}==>  {Style.NORMAL}Transcoding `{file}` to ogg/opus.")
    processed_files.append(transcode_to_opus(file))
    durations.append(librosa.get_duration(path=file))

  num_sounds = int(input(f"{Style.BRIGHT}{Fore.GREEN}Enter number of sounds to add in total (recommended 15-60 per 1h): {Style.RESET_ALL}"))
  duration = input(f"{Style.BRIGHT}{Fore.GREEN}Enter output duration [3600s]: {Style.RESET_ALL}")
  if duration == "":
    duration = 3600
  else:
    duration = float(duration.rstrip("s"))
  
  # generate indices for the sounds
  indices = list(islice(gap_random_uniform(0, duration-max(durations), max(durations)+1), num_sounds))
  indices.sort()

  # setup loop vars
  files_durations = list(zip(processed_files, durations))
  prev = 0
  result_files = []

  # add the silence-sound thingies
  for i, curr in enumerate(indices):
    f, d = random.choice(files_durations)
    print(f"{Fore.BLUE}{Style.DIM}=>  {Style.NORMAL}Selected sound clip `{f}`")
    sd = (curr)-prev # silence duration
    print(f"{Fore.BLUE}{Style.DIM}=>  {Style.NORMAL}Generating {sd}s silence")
    silence = generate_silence(sd)
    prev = curr + d
    result_files.extend([silence, f])
  
  # add the last silence
  print(f"{Fore.BLUE}{Style.DIM}=>  {Style.NORMAL}Generating final silence")
  silence = generate_silence(duration-prev)
  result_files.append(silence)

  # concatenate the files
  print(f"{Fore.YELLOW}{Style.NORMAL}==>  {Style.BRIGHT}Concatenating {len(result_files)} files...")


  stream = ffmpeg.concat(*[ffmpeg.input(rf) for rf in result_files], a=1, n=2, v=0)

  file_id = [chr(random.choice([0x61, 0x41])+random.randint(0,25)) for _ in range(6)]
  outfile = f"{num_sounds}_{int(duration)}s_silence_{''.join(file_id)}"

  stream = stream.output(f"{outfile}.m4a", acodec=AUDIO_ENC, audio_bitrate=192_000)

  stream.run(quiet=True)
  print(f"{Fore.YELLOW}{Style.NORMAL}==>  {Style.BRIGHT}Successfully concatenated audio: `{outfile}.m4a`\n")

  print(f"{Fore.YELLOW}{Style.NORMAL}==>  {Style.BRIGHT}Writing audio metadata...")

  audio_file = MP4(f"{outfile}.m4a")

  # tag the file

  audio_file["\xa9gen"] = "Shitpost"
  audio_file["\xa9cmt"] = "Generated using BrokenSilence"
  audio_file["\xa9day"] = str(datetime.now().strftime("%Y-%m-%d"))
  audio_file["\xa9ART"] = "EvilSquirrelGuy"
  audio_file["\xa9wrt"] = "EvilSquirrelGuy"
  audio_file["purl"] = "https://www.github.com/EvilSquirrelGuy/BrokenSilence"

  audio_file["\xa9lyr"] = ', '.join([af.lstrip("sounds")[1:] for af in audio_files])

  # convert and crop the image
  thumb = Image.open(img)
  thumb_path = os.path.join(".tmp", "thumbnail")

  (w, h) = thumb.size

  new_size = min(w, h)

  left = (w-new_size)/2
  top = (h-new_size)/2
  right = (w+new_size)/2
  bottom = (h+new_size)/2

  thumb = thumb.crop((left, top, right, bottom))
  thumb.thumbnail((1024, 1024))

  thumb.save(thumb_path, "PNG")

  with open(thumb_path, "rb") as thumb_bin:
    audio_file["covr"] = [
      MP4Cover(thumb_bin.read(), imageformat=MP4Cover.FORMAT_PNG)
    ]
  
  audio_file.save()

  print(f"{Fore.BLUE}{Style.DIM}==>  {Style.NORMAL}Cleaning temporary files...")
  shutil.rmtree(".tmp")
  # os.remove(f"{outfile}.na.m4a")

  print(f"\n\n{Style.BRIGHT}{Fore.GREEN}Time to generate a video!{Style.RESET_ALL}")
  print(f"{Fore.RED}{Style.BRIGHT}WARNING: {Style.RESET_ALL}{Fore.RED}This process may take quite long depending on your system and the video duration. Also the resulting filesize may be quite large (~200MB/1hr).\n{Style.RESET_ALL}")

  input(f"\n{Style.DIM}Press Enter to continue...{Style.RESET_ALL}")
  print()

  print(f"{Fore.YELLOW}{Style.NORMAL}==>  {Style.BRIGHT}Generating code for video...")

  img_stream = ffmpeg.input(img, loop=1, framerate=1)
  audio_stream = ffmpeg.input(f"{outfile}.m4a")

  img_stream = ffmpeg.filter(img_stream, "scale", "1920", "1080", force_original_aspect_ratio="decrease")
  img_stream = ffmpeg.filter(img_stream, "pad", "1920", "1080", "-1", "-1")
  
  vid_stream = ffmpeg.output(img_stream, audio_stream.audio, f"{outfile}.mp4", acodec="copy", vcodec=VIDEO_ENC, pix_fmt="yuv420p", shortest=None, tune="stillimage", preset="fast")


  vid_stream.run()
  print(f"{Fore.YELLOW}{Style.NORMAL}==>  {Style.BRIGHT}Successfully created file: `{outfile}.mp4`\n")
  print(f"{Fore.YELLOW}{Style.NORMAL}==>  {Style.BRIGHT}Writing video metadata...")

  video_file = MP4(f"{outfile}.mp4")

  video_file["\xa9gen"] = "Shitpost"
  video_file["\xa9cmt"] = "Generated using BrokenSilence"
  video_file["desc"] = ("Generated using BrokenSilence\n"
    "https://www.github.com/EvilSquirrelGuy/BrokenSilence\n\n"
    f"Duration: {duration} seconds\n"
    f"No. of sounds: {num_sounds}\n"
    "Sound files used:\n- "
    '\n- '.join([af.lstrip("sounds")[1:] for af in audio_files])
    )
  video_file["\xa9day"] = str(datetime.now().strftime("%Y-%m-%d"))
  video_file["\xa9ART"] = "EvilSquirrelGuy"

  cov_bfr = BytesIO()
  cov_img = Image.open(img)
  cov_img.save(cov_bfr, "PNG")
  cov_bfr.name = "cover.png"
  cov_bfr.seek(0)

  video_file["covr"] = [
    MP4Cover(cov_bfr.read(), imageformat=MP4Cover.FORMAT_PNG)
  ]

  video_file.save()

  print(f"{Fore.YELLOW}{Style.NORMAL}==>  {Style.BRIGHT}Finished creating video.")



if __name__ == "__main__":
  main()