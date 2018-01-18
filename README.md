Timelapse-Video-for-3D-printer
==============================

Creates Time lapse Videos for Sindoh 3DWOX D200 Printers

This python 2.7 program is a command line utility for creating Time lapse videos of the 3D printing process for network connected Sindoh 3DWOX D200 printers.
It may work on other version of the printer (D201 for example) but is untested (as I only have the D200).

This is version 1.0 so it may be buggy!

**NOTE: This program is written for Python 2.7, it will not work on Python 3.X without some fixing**

Tested with:
* Ubuntu 14.04
* Windows 10

## Features
* Configurable minimum frame rate
* Configurable maximum time (for time lapse video)
* Requires printer ip address
* Records using OpenCV or ffmpeg
* Video includes text of all main printer variables
* Can be run in "daemon mode" so it runs continually, and records all prints
* If filename not specified, uses the model name as the filename
* Will not overwrite existing files (adds "-number", to existing file names)
* Gives "bar graph" progress display on the command line by default, with useful print statistics.
* Configurable postroll (seconds of video after print finished)
* Works on linux and Windows

## Screen Shots
![Video Starting](/start_video.jpg)
![Video towards the end](/midway_video.jpg)
![Console Output](/console.jpg)

### OpenCV
This program uses OpenCV 3.x (tested with 3.2)

## Dependencies
The following libraries/modules are used:
* openCV      *required*
* numpy       *required (used by openCV)*

You can install OpenCV as follows:
```bash
<sudo> pip install opencv-python
```

## Install
First you need python 2.7 and then:

Clone this repository:
```bash
git clone https://github.com/NickWaterton/Timelapse-Video-for-3D-printer.git
cd Timelapse-Video-for-3D-printer
```

run `./record_3dprint.py -h` (or `python ./record_3dprint.py -h` to get the available options. This is what you will get:

```bash
usage: record_3dprint.py [-h] [-o OUT] [-od OUTDIRECTORY] [-f FPS] [-t TIME]
                         [-u URL] [-p PORT] [-pr POSTROLL] [-l LOG] [-d]
                         [-Fx FFMPEGEXECUTABLE] [-P | -F] [-R] [-Q QUALITY]
                         [-X] [-D] [-V]

Record time lapse video of 3DWOX printer in action

optional arguments:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     Destination File Name defaults to the model name.avi
  -od OUTDIRECTORY, --outdirectory OUTDIRECTORY
                        Destination directory (default=current directory)
  -f FPS, --fps FPS     min playback speed, 1=real time, 10=10X real time etc
                        default=10
  -t TIME, --time TIME  optional max recording time in seconds. 0=unlimited.
                        Set max duration of video, and fps is calculated
                        automatically (but not less than min frame rate).
                        Default=300
  -u URL, --url URL     url/IP to read image from (default=192.168.100.204)
  -p PORT, --port PORT  url port (default=80)
  -pr POSTROLL, --postroll POSTROLL
                        seconds of video to capture after print complete
                        (default=5)
  -l LOG, --log LOG     main log file. Set to None to disable logging.
                        (default=~/3DPrinter_video.log)
  -d, --daemon          run as daemon (ie never exit, just loop)
  -Fx FFMPEGEXECUTABLE, --ffmpegexecutable FFMPEGEXECUTABLE
                        path and name of ffmpeg executable(default=ffmpeg)
  -P, --postprocess     post process video file with ffmpeg to reduce size
  -F, --ffmpeg          use ffmpeg for writing file (not OpenCV)
  -R, --deleteoriginal  delete original file after post processing video file
                        with ffmpeg
  -Q QUALITY, --quality QUALITY
                        ffmpeg record Quality, lower is better (but bigger
                        file), max 31 default=30
  -X, --force           force record (for debugging) without checking status
  -D, --debug           debug mode
  -V, --version         show program's version number and exit
```

## quick start
With the printer ready to print, but not printing (and connected to wifi/ethernet), enter
```bash
./record_3dprint.py -u x.x.x.x
```
or
```bash
python record_3dprint. -u x.x.x.x
```

where x.x.x.x is the ip address of your printer. This will start up in idle mode:
```bash
****** Program Started ********
Logging to file: /home/nick/3DPrinter_video.log
waiting for printer response...
Printer online, status: 10004 (idle)
Waiting to start Recording, please send/load file to printer
```

on windows:
```bash
****** Program Started ********
Logging to file: C:\Users\nickw/3DPrinter_video.log
waiting for printer response...
Printer online, status: 10004 (idle)
Waiting to start Recording, please send/load file to printer
```

if you send a file to the printer, the console should change to:

```bash
Writing AVI file reg_litho_3cm[766]-2.avi
Printing: reg_litho_3cm[766], Material:PLA, colour:White, from:Local Output: OpenCV Output.
Recording at 10X realtime (min framerate 10X, max duration: 0:05:00, actual duration: 0:02:11). Estimated print time: 0:0, completed at: 2018-01-17 17:15:28
reg_litho_3cm[766]-2.avi |████████████████████████████████████████| 100% time remaining 0:0, remaining fil: 17% 0:11:07 
```

This example is the end of a print, normally the bar graph will start at the beginning and 0%. The name of the model (filename sent to print) will be used as the default output file, and the default extension is ".avi".
You can use `<CNTRL> C` to exit.

This will record a *HUGE* MJPEG file. A better way to create video files is to use ffmpeg, and a copy of the windows ffmpeg (ffmpeg.exe) is included with this repository. Ubuntu people, install ffmpeg using:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

Or any of the other zillions of ways to get ffmpeg in Ubuntu.

## Usage
If the ffmpeg executable is not in your path, you need to specify the location and name of the ffmpeg executable on the command line. You don't need to do this if the executable is in the current directory.
You can now generate an .mp4 file time lapse video like this:

```bash
./record_3dprint.py -u x.x.x.x -F -Fx /path-to-ffmpeg/ffmpeg
```

or (windows)
```bash
python record_3dprint.py -u x.x.x.x -F -Fx "C:\path to ffmpeg\ffmpeg.exe"
```

default file name is now ".mp4"

You can use `-F` or `-P`, -F causes the .mp4 to be created directly, -P creates a temporary Huge MJPG, then at the end of the recording, converts it to a ".mp4" file, and makes it suitable for web streaming. This obviously uses vastly more disk space than creating the (relatively) small ".mp4" file directly.

You can also specify the location and name of the output file using the `-o` option. The type of file is dictated by the extension. I have tested ".mkv", ".mov", ".avi", ".mp4".

You can specify the name and location of the log file using the `-l` option. Setting this to 'none', results in no log file.

Using the `-od` option allows the output directory to be specified, default is the current directory. You could specify this in the filename, but this option allows you to specify the directory, while the filenames are automatically generated. Don't include a path in the filename, if you are using the `-od` option.

You have to enclose pathnames in `""` if there are spaces in the pathnames.

The maximum length (in seconds) of the time lapse video is 5 minutes by default, it may be shorter (for a print of less that 50 minutes), you can set this to whatever you like using the `-t` option, and the fps (frames per second) will be adjusted accordingly. Setting this to 0 results in a video of unlimited length.

The `-Q` option only works with ffmpeg output, and sets the quality of the video, value is 1-31, with 1 being the best, and 31 the worst. 30 is the default. The better the quality of the video, the bigger the file generated.

Normally the program will exit when the print is done. Adding the `-d` modifier makes the program loop, so it will keep outputting videos every time you send a file to print. If you leave the `-o` off, the filenames are generated automatically.

The `-D` and `-X` options are for debugging, `-X` forces the program to start recording, even if the printer is not printing, and can be used for testing. the `-D` option replaces the bar graph with debug text.


An example output video (reg_litho_3cm[766].mp4) is included so you can see how it looks.