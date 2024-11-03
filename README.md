# BrokenSilence
create your own "1 hour of silence randomly interrupted by &lt;sound>" videos!

> [!IMPORTANT]
> The quality for this code is actually horrible, I know. I threw this together
> in a couple hours over a weekend, cuz why spend 1h in a video editor when you
> could spend a whole day automating it!

Also this probably won't be maintained or rewritten, but feel free to open a PR anyway. I'll
gladly accept people spending their time on making annoying your friends easier :p

## Usage

To run the program, make sure you have python 3.12 installed, then simply run:

`./run.sh` if you're on macOS, Linux or some other *nix

or

`run.bat` if you're on Windows.


Then follow the instructions printed in your terminal :)


## Adding Sound files

This script will randomly select files from the `sounds/` folder to play every so often.

The following file extensions are supported (i.e. read by the script, it uses ffmpeg so it shouldnt be an issue):
* .mp3
* .m4a
* .ogg
* .flac
* .wav
* .opus


## Adding an Image

The script will prompt you to select an image from the `images/` directory to use as the following:
* Audio file thumbnail (will be cropped to a square)
* Video content
* Video thumbnail

It supports the following extensions:
* .jpg/.jpeg
* .png
* .tif/.tiff
* .bmp


## Outputted files

The script will generate an audio file and a video, both tagged and thumbailed so you can share the video.
Since the files are so long (~1hr), you can expect the results to take up about 300MB on your disk per hour.
(100MB for the m4a file and 200 MB for the video).

The video is MP4 (HEVC/AAC) (1fps) and audio is M4A (AAC 192kbps), the encoder will vary by what is available on your
platform, though feel free to modify the script to select a different encoder if you want to speed up the script.


## Examples

* [1 hour of silence broken up by various sounds (playlist)](https://youtube.com/playlist?list=PLYwid3dI6PP2Sy9DUtMoj5ZpLJqD88D4p)
