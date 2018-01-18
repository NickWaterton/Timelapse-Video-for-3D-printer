#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Original Author Nick Waterton P.Eng Jan 17th 2018
program to record 3Dprinting from Sindoh DP200 3DWOX

NOTE: this program requires OpenCV 3.x
      and numpy, also ffmpeg is very useful!
      THIS PROGRAM IS A PYTHON 2.7 PROGRAM it will not work in python 3.x without some fixing!
      
NOTE: Running this program continually will keep the light on your printer all the time (if you have it set to "only on when printing").
      Web access turns the light on for 15s after the access.


url for jpeg image is http://myprinterIP/?action=snapshot or http://myprinterIP/?action=snapshot&n=15000000 where 150000000 is unix timestamp.
data url http://myprinterIP/cgi-bin/config_periodic_data.cgi

V 1.01  NW 18/1/2018    Updated output directory option
'''

from __future__ import print_function

import argparse
import urllib2, socket
import cv2
import numpy as np
import os, sys
import time, datetime
import subprocess
import threading
import logging
from logging.handlers import RotatingFileHandler

__version__ = "1.01"

""" 
Original Author  Ernesto P. Adorio, Ph.D 
Original Source: http://my-other-life-as-programmer.blogspot.com/2012/02/python-finding-nearest-matching-color.html
Modifed By: JDiscar
This class maps an RGB value to the nearest color name it can find. Code is modified to include 
ImageMagick names and WebColor names.  
1. Modify the minimization criterion to use least sum of squares of the differences.
2. Provide error checking for input R, G, B values to be within the interval [0, 255].
3. Provide different ways to specify the input RGB values, aside from the (R, G, B) values as done in the program above.
"""
class ColorNames:
    # Src: http://www.w3schools.com/html/html_colornames.asp  
    WebColorMap = {}
    WebColorMap["AliceBlue"] = "#F0F8FF"
    WebColorMap["AntiqueWhite"] = "#FAEBD7"
    WebColorMap["Aqua"] = "#00FFFF"
    WebColorMap["Aquamarine"] = "#7FFFD4"
    WebColorMap["Azure"] = "#F0FFFF"
    WebColorMap["Beige"] = "#F5F5DC"
    WebColorMap["Bisque"] = "#FFE4C4"
    WebColorMap["Black"] = "#000000"
    WebColorMap["BlanchedAlmond"] = "#FFEBCD"
    WebColorMap["Blue"] = "#0000FF"
    WebColorMap["BlueViolet"] = "#8A2BE2"
    WebColorMap["Brown"] = "#A52A2A"
    WebColorMap["BurlyWood"] = "#DEB887"
    WebColorMap["CadetBlue"] = "#5F9EA0"
    WebColorMap["Chartreuse"] = "#7FFF00"
    WebColorMap["Chocolate"] = "#D2691E"
    WebColorMap["Coral"] = "#FF7F50"
    WebColorMap["CornflowerBlue"] = "#6495ED"
    WebColorMap["Cornsilk"] = "#FFF8DC"
    WebColorMap["Crimson"] = "#DC143C"
    WebColorMap["Cyan"] = "#00FFFF"
    WebColorMap["DarkBlue"] = "#00008B"
    WebColorMap["DarkCyan"] = "#008B8B"
    WebColorMap["DarkGoldenRod"] = "#B8860B"
    WebColorMap["DarkGray"] = "#A9A9A9"
    WebColorMap["DarkGrey"] = "#A9A9A9"
    WebColorMap["DarkGreen"] = "#006400"
    WebColorMap["DarkKhaki"] = "#BDB76B"
    WebColorMap["DarkMagenta"] = "#8B008B"
    WebColorMap["DarkOliveGreen"] = "#556B2F"
    WebColorMap["Darkorange"] = "#FF8C00"
    WebColorMap["DarkOrchid"] = "#9932CC"
    WebColorMap["DarkRed"] = "#8B0000"
    WebColorMap["DarkSalmon"] = "#E9967A"
    WebColorMap["DarkSeaGreen"] = "#8FBC8F"
    WebColorMap["DarkSlateBlue"] = "#483D8B"
    WebColorMap["DarkSlateGray"] = "#2F4F4F"
    WebColorMap["DarkSlateGrey"] = "#2F4F4F"
    WebColorMap["DarkTurquoise"] = "#00CED1"
    WebColorMap["DarkViolet"] = "#9400D3"
    WebColorMap["DeepPink"] = "#FF1493"
    WebColorMap["DeepSkyBlue"] = "#00BFFF"
    WebColorMap["DimGray"] = "#696969"
    WebColorMap["DimGrey"] = "#696969"
    WebColorMap["DodgerBlue"] = "#1E90FF"
    WebColorMap["FireBrick"] = "#B22222"
    WebColorMap["FloralWhite"] = "#FFFAF0"
    WebColorMap["ForestGreen"] = "#228B22"
    WebColorMap["Fuchsia"] = "#FF00FF"
    WebColorMap["Gainsboro"] = "#DCDCDC"
    WebColorMap["GhostWhite"] = "#F8F8FF"
    WebColorMap["Gold"] = "#FFD700"
    WebColorMap["GoldenRod"] = "#DAA520"
    WebColorMap["Gray"] = "#808080"
    WebColorMap["Grey"] = "#808080"
    WebColorMap["Green"] = "#008000"
    WebColorMap["GreenYellow"] = "#ADFF2F"
    WebColorMap["HoneyDew"] = "#F0FFF0"
    WebColorMap["HotPink"] = "#FF69B4"
    WebColorMap["IndianRed"] = "#CD5C5C"
    WebColorMap["Indigo"] = "#4B0082"
    WebColorMap["Ivory"] = "#FFFFF0"
    WebColorMap["Khaki"] = "#F0E68C"
    WebColorMap["Lavender"] = "#E6E6FA"
    WebColorMap["LavenderBlush"] = "#FFF0F5"
    WebColorMap["LawnGreen"] = "#7CFC00"
    WebColorMap["LemonChiffon"] = "#FFFACD"
    WebColorMap["LightBlue"] = "#ADD8E6"
    WebColorMap["LightCoral"] = "#F08080"
    WebColorMap["LightCyan"] = "#E0FFFF"
    WebColorMap["LightGoldenRodYellow"] = "#FAFAD2"
    WebColorMap["LightGray"] = "#D3D3D3"
    WebColorMap["LightGrey"] = "#D3D3D3"
    WebColorMap["LightGreen"] = "#90EE90"
    WebColorMap["LightPink"] = "#FFB6C1"
    WebColorMap["LightSalmon"] = "#FFA07A"
    WebColorMap["LightSeaGreen"] = "#20B2AA"
    WebColorMap["LightSkyBlue"] = "#87CEFA"
    WebColorMap["LightSlateGray"] = "#778899"
    WebColorMap["LightSlateGrey"] = "#778899"
    WebColorMap["LightSteelBlue"] = "#B0C4DE"
    WebColorMap["LightYellow"] = "#FFFFE0"
    WebColorMap["Lime"] = "#00FF00"
    WebColorMap["LimeGreen"] = "#32CD32"
    WebColorMap["Linen"] = "#FAF0E6"
    WebColorMap["Magenta"] = "#FF00FF"
    WebColorMap["Maroon"] = "#800000"
    WebColorMap["MediumAquaMarine"] = "#66CDAA"
    WebColorMap["MediumBlue"] = "#0000CD"
    WebColorMap["MediumOrchid"] = "#BA55D3"
    WebColorMap["MediumPurple"] = "#9370D8"
    WebColorMap["MediumSeaGreen"] = "#3CB371"
    WebColorMap["MediumSlateBlue"] = "#7B68EE"
    WebColorMap["MediumSpringGreen"] = "#00FA9A"
    WebColorMap["MediumTurquoise"] = "#48D1CC"
    WebColorMap["MediumVioletRed"] = "#C71585"
    WebColorMap["MidnightBlue"] = "#191970"
    WebColorMap["MintCream"] = "#F5FFFA"
    WebColorMap["MistyRose"] = "#FFE4E1"
    WebColorMap["Moccasin"] = "#FFE4B5"
    WebColorMap["NavajoWhite"] = "#FFDEAD"
    WebColorMap["Navy"] = "#000080"
    WebColorMap["OldLace"] = "#FDF5E6"
    WebColorMap["Olive"] = "#808000"
    WebColorMap["OliveDrab"] = "#6B8E23"
    WebColorMap["Orange"] = "#FFA500"
    WebColorMap["OrangeRed"] = "#FF4500"
    WebColorMap["Orchid"] = "#DA70D6"
    WebColorMap["PaleGoldenRod"] = "#EEE8AA"
    WebColorMap["PaleGreen"] = "#98FB98"
    WebColorMap["PaleTurquoise"] = "#AFEEEE"
    WebColorMap["PaleVioletRed"] = "#D87093"
    WebColorMap["PapayaWhip"] = "#FFEFD5"
    WebColorMap["PeachPuff"] = "#FFDAB9"
    WebColorMap["Peru"] = "#CD853F"
    WebColorMap["Pink"] = "#FFC0CB"
    WebColorMap["Plum"] = "#DDA0DD"
    WebColorMap["PowderBlue"] = "#B0E0E6"
    WebColorMap["Purple"] = "#800080"
    WebColorMap["Red"] = "#FF0000"
    WebColorMap["RosyBrown"] = "#BC8F8F"
    WebColorMap["RoyalBlue"] = "#4169E1"
    WebColorMap["SaddleBrown"] = "#8B4513"
    WebColorMap["Salmon"] = "#FA8072"
    WebColorMap["SandyBrown"] = "#F4A460"
    WebColorMap["SeaGreen"] = "#2E8B57"
    WebColorMap["SeaShell"] = "#FFF5EE"
    WebColorMap["Sienna"] = "#A0522D"
    WebColorMap["Silver"] = "#C0C0C0"
    WebColorMap["SkyBlue"] = "#87CEEB"
    WebColorMap["SlateBlue"] = "#6A5ACD"
    WebColorMap["SlateGray"] = "#708090"
    WebColorMap["SlateGrey"] = "#708090"
    WebColorMap["Snow"] = "#FFFAFA"
    WebColorMap["SpringGreen"] = "#00FF7F"
    WebColorMap["SteelBlue"] = "#4682B4"
    WebColorMap["Tan"] = "#D2B48C"
    WebColorMap["Teal"] = "#008080"
    WebColorMap["Thistle"] = "#D8BFD8"
    WebColorMap["Tomato"] = "#FF6347"
    WebColorMap["Turquoise"] = "#40E0D0"
    WebColorMap["Violet"] = "#EE82EE"
    WebColorMap["Wheat"] = "#F5DEB3"
    WebColorMap["White"] = "#FFFFFF"
    WebColorMap["WhiteSmoke"] = "#F5F5F5"
    WebColorMap["Yellow"] = "#FFFF00"
    WebColorMap["YellowGreen"] = "#9ACD32"
    
    # src: http://www.imagemagick.org/script/color.php
    ImageMagickColorMap = {}
    ImageMagickColorMap["snow"] = "#FFFAFA"
    ImageMagickColorMap["snow1"] = "#FFFAFA"
    ImageMagickColorMap["snow2"] = "#EEE9E9"
    ImageMagickColorMap["RosyBrown1"] = "#FFC1C1"
    ImageMagickColorMap["RosyBrown2"] = "#EEB4B4"
    ImageMagickColorMap["snow3"] = "#CDC9C9"
    ImageMagickColorMap["LightCoral"] = "#F08080"
    ImageMagickColorMap["IndianRed1"] = "#FF6A6A"
    ImageMagickColorMap["RosyBrown3"] = "#CD9B9B"
    ImageMagickColorMap["IndianRed2"] = "#EE6363"
    ImageMagickColorMap["RosyBrown"] = "#BC8F8F"
    ImageMagickColorMap["brown1"] = "#FF4040"
    ImageMagickColorMap["firebrick1"] = "#FF3030"
    ImageMagickColorMap["brown2"] = "#EE3B3B"
    ImageMagickColorMap["IndianRed"] = "#CD5C5C"
    ImageMagickColorMap["IndianRed3"] = "#CD5555"
    ImageMagickColorMap["firebrick2"] = "#EE2C2C"
    ImageMagickColorMap["snow4"] = "#8B8989"
    ImageMagickColorMap["brown3"] = "#CD3333"
    ImageMagickColorMap["red"] = "#FF0000"
    ImageMagickColorMap["red1"] = "#FF0000"
    ImageMagickColorMap["RosyBrown4"] = "#8B6969"
    ImageMagickColorMap["firebrick3"] = "#CD2626"
    ImageMagickColorMap["red2"] = "#EE0000"
    ImageMagickColorMap["firebrick"] = "#B22222"
    ImageMagickColorMap["brown"] = "#A52A2A"
    ImageMagickColorMap["red3"] = "#CD0000"
    ImageMagickColorMap["IndianRed4"] = "#8B3A3A"
    ImageMagickColorMap["brown4"] = "#8B2323"
    ImageMagickColorMap["firebrick4"] = "#8B1A1A"
    ImageMagickColorMap["DarkRed"] = "#8B0000"
    ImageMagickColorMap["red4"] = "#8B0000"
    ImageMagickColorMap["maroon"] = "#800000"
    ImageMagickColorMap["LightPink1"] = "#FFAEB9"
    ImageMagickColorMap["LightPink3"] = "#CD8C95"
    ImageMagickColorMap["LightPink4"] = "#8B5F65"
    ImageMagickColorMap["LightPink2"] = "#EEA2AD"
    ImageMagickColorMap["LightPink"] = "#FFB6C1"
    ImageMagickColorMap["pink"] = "#FFC0CB"
    ImageMagickColorMap["crimson"] = "#DC143C"
    ImageMagickColorMap["pink1"] = "#FFB5C5"
    ImageMagickColorMap["pink2"] = "#EEA9B8"
    ImageMagickColorMap["pink3"] = "#CD919E"
    ImageMagickColorMap["pink4"] = "#8B636C"
    ImageMagickColorMap["PaleVioletRed4"] = "#8B475D"
    ImageMagickColorMap["PaleVioletRed"] = "#DB7093"
    ImageMagickColorMap["PaleVioletRed2"] = "#EE799F"
    ImageMagickColorMap["PaleVioletRed1"] = "#FF82AB"
    ImageMagickColorMap["PaleVioletRed3"] = "#CD6889"
    ImageMagickColorMap["LavenderBlush"] = "#FFF0F5"
    ImageMagickColorMap["LavenderBlush1"] = "#FFF0F5"
    ImageMagickColorMap["LavenderBlush3"] = "#CDC1C5"
    ImageMagickColorMap["LavenderBlush2"] = "#EEE0E5"
    ImageMagickColorMap["LavenderBlush4"] = "#8B8386"
    ImageMagickColorMap["maroon"] = "#B03060"
    ImageMagickColorMap["HotPink3"] = "#CD6090"
    ImageMagickColorMap["VioletRed3"] = "#CD3278"
    ImageMagickColorMap["VioletRed1"] = "#FF3E96"
    ImageMagickColorMap["VioletRed2"] = "#EE3A8C"
    ImageMagickColorMap["VioletRed4"] = "#8B2252"
    ImageMagickColorMap["HotPink2"] = "#EE6AA7"
    ImageMagickColorMap["HotPink1"] = "#FF6EB4"
    ImageMagickColorMap["HotPink4"] = "#8B3A62"
    ImageMagickColorMap["HotPink"] = "#FF69B4"
    ImageMagickColorMap["DeepPink"] = "#FF1493"
    ImageMagickColorMap["DeepPink1"] = "#FF1493"
    ImageMagickColorMap["DeepPink2"] = "#EE1289"
    ImageMagickColorMap["DeepPink3"] = "#CD1076"
    ImageMagickColorMap["DeepPink4"] = "#8B0A50"
    ImageMagickColorMap["maroon1"] = "#FF34B3"
    ImageMagickColorMap["maroon2"] = "#EE30A7"
    ImageMagickColorMap["maroon3"] = "#CD2990"
    ImageMagickColorMap["maroon4"] = "#8B1C62"
    ImageMagickColorMap["MediumVioletRed"] = "#C71585"
    ImageMagickColorMap["VioletRed"] = "#D02090"
    ImageMagickColorMap["orchid2"] = "#EE7AE9"
    ImageMagickColorMap["orchid"] = "#DA70D6"
    ImageMagickColorMap["orchid1"] = "#FF83FA"
    ImageMagickColorMap["orchid3"] = "#CD69C9"
    ImageMagickColorMap["orchid4"] = "#8B4789"
    ImageMagickColorMap["thistle1"] = "#FFE1FF"
    ImageMagickColorMap["thistle2"] = "#EED2EE"
    ImageMagickColorMap["plum1"] = "#FFBBFF"
    ImageMagickColorMap["plum2"] = "#EEAEEE"
    ImageMagickColorMap["thistle"] = "#D8BFD8"
    ImageMagickColorMap["thistle3"] = "#CDB5CD"
    ImageMagickColorMap["plum"] = "#DDA0DD"
    ImageMagickColorMap["violet"] = "#EE82EE"
    ImageMagickColorMap["plum3"] = "#CD96CD"
    ImageMagickColorMap["thistle4"] = "#8B7B8B"
    ImageMagickColorMap["fuchsia"] = "#FF00FF"
    ImageMagickColorMap["magenta"] = "#FF00FF"
    ImageMagickColorMap["magenta1"] = "#FF00FF"
    ImageMagickColorMap["plum4"] = "#8B668B"
    ImageMagickColorMap["magenta2"] = "#EE00EE"
    ImageMagickColorMap["magenta3"] = "#CD00CD"
    ImageMagickColorMap["DarkMagenta"] = "#8B008B"
    ImageMagickColorMap["magenta4"] = "#8B008B"
    ImageMagickColorMap["purple"] = "#800080"
    ImageMagickColorMap["MediumOrchid"] = "#BA55D3"
    ImageMagickColorMap["MediumOrchid1"] = "#E066FF"
    ImageMagickColorMap["MediumOrchid2"] = "#D15FEE"
    ImageMagickColorMap["MediumOrchid3"] = "#B452CD"
    ImageMagickColorMap["MediumOrchid4"] = "#7A378B"
    ImageMagickColorMap["DarkViolet"] = "#9400D3"
    ImageMagickColorMap["DarkOrchid"] = "#9932CC"
    ImageMagickColorMap["DarkOrchid1"] = "#BF3EFF"
    ImageMagickColorMap["DarkOrchid3"] = "#9A32CD"
    ImageMagickColorMap["DarkOrchid2"] = "#B23AEE"
    ImageMagickColorMap["DarkOrchid4"] = "#68228B"
    ImageMagickColorMap["purple"] = "#A020F0"
    ImageMagickColorMap["indigo"] = "#4B0082"
    ImageMagickColorMap["BlueViolet"] = "#8A2BE2"
    ImageMagickColorMap["purple2"] = "#912CEE"
    ImageMagickColorMap["purple3"] = "#7D26CD"
    ImageMagickColorMap["purple4"] = "#551A8B"
    ImageMagickColorMap["purple1"] = "#9B30FF"
    ImageMagickColorMap["MediumPurple"] = "#9370DB"
    ImageMagickColorMap["MediumPurple1"] = "#AB82FF"
    ImageMagickColorMap["MediumPurple2"] = "#9F79EE"
    ImageMagickColorMap["MediumPurple3"] = "#8968CD"
    ImageMagickColorMap["MediumPurple4"] = "#5D478B"
    ImageMagickColorMap["DarkSlateBlue"] = "#483D8B"
    ImageMagickColorMap["LightSlateBlue"] = "#8470FF"
    ImageMagickColorMap["MediumSlateBlue"] = "#7B68EE"
    ImageMagickColorMap["SlateBlue"] = "#6A5ACD"
    ImageMagickColorMap["SlateBlue1"] = "#836FFF"
    ImageMagickColorMap["SlateBlue2"] = "#7A67EE"
    ImageMagickColorMap["SlateBlue3"] = "#6959CD"
    ImageMagickColorMap["SlateBlue4"] = "#473C8B"
    ImageMagickColorMap["GhostWhite"] = "#F8F8FF"
    ImageMagickColorMap["lavender"] = "#E6E6FA"
    ImageMagickColorMap["blue"] = "#0000FF"
    ImageMagickColorMap["blue1"] = "#0000FF"
    ImageMagickColorMap["blue2"] = "#0000EE"
    ImageMagickColorMap["blue3"] = "#0000CD"
    ImageMagickColorMap["MediumBlue"] = "#0000CD"
    ImageMagickColorMap["blue4"] = "#00008B"
    ImageMagickColorMap["DarkBlue"] = "#00008B"
    ImageMagickColorMap["MidnightBlue"] = "#191970"
    ImageMagickColorMap["navy"] = "#000080"
    ImageMagickColorMap["NavyBlue"] = "#000080"
    ImageMagickColorMap["RoyalBlue"] = "#4169E1"
    ImageMagickColorMap["RoyalBlue1"] = "#4876FF"
    ImageMagickColorMap["RoyalBlue2"] = "#436EEE"
    ImageMagickColorMap["RoyalBlue3"] = "#3A5FCD"
    ImageMagickColorMap["RoyalBlue4"] = "#27408B"
    ImageMagickColorMap["CornflowerBlue"] = "#6495ED"
    ImageMagickColorMap["LightSteelBlue"] = "#B0C4DE"
    ImageMagickColorMap["LightSteelBlue1"] = "#CAE1FF"
    ImageMagickColorMap["LightSteelBlue2"] = "#BCD2EE"
    ImageMagickColorMap["LightSteelBlue3"] = "#A2B5CD"
    ImageMagickColorMap["LightSteelBlue4"] = "#6E7B8B"
    ImageMagickColorMap["SlateGray4"] = "#6C7B8B"
    ImageMagickColorMap["SlateGray1"] = "#C6E2FF"
    ImageMagickColorMap["SlateGray2"] = "#B9D3EE"
    ImageMagickColorMap["SlateGray3"] = "#9FB6CD"
    ImageMagickColorMap["LightSlateGray"] = "#778899"
    ImageMagickColorMap["LightSlateGrey"] = "#778899"
    ImageMagickColorMap["SlateGray"] = "#708090"
    ImageMagickColorMap["SlateGrey"] = "#708090"
    ImageMagickColorMap["DodgerBlue"] = "#1E90FF"
    ImageMagickColorMap["DodgerBlue1"] = "#1E90FF"
    ImageMagickColorMap["DodgerBlue2"] = "#1C86EE"
    ImageMagickColorMap["DodgerBlue4"] = "#104E8B"
    ImageMagickColorMap["DodgerBlue3"] = "#1874CD"
    ImageMagickColorMap["AliceBlue"] = "#F0F8FF"
    ImageMagickColorMap["SteelBlue4"] = "#36648B"
    ImageMagickColorMap["SteelBlue"] = "#4682B4"
    ImageMagickColorMap["SteelBlue1"] = "#63B8FF"
    ImageMagickColorMap["SteelBlue2"] = "#5CACEE"
    ImageMagickColorMap["SteelBlue3"] = "#4F94CD"
    ImageMagickColorMap["SkyBlue4"] = "#4A708B"
    ImageMagickColorMap["SkyBlue1"] = "#87CEFF"
    ImageMagickColorMap["SkyBlue2"] = "#7EC0EE"
    ImageMagickColorMap["SkyBlue3"] = "#6CA6CD"
    ImageMagickColorMap["LightSkyBlue"] = "#87CEFA"
    ImageMagickColorMap["LightSkyBlue4"] = "#607B8B"
    ImageMagickColorMap["LightSkyBlue1"] = "#B0E2FF"
    ImageMagickColorMap["LightSkyBlue2"] = "#A4D3EE"
    ImageMagickColorMap["LightSkyBlue3"] = "#8DB6CD"
    ImageMagickColorMap["SkyBlue"] = "#87CEEB"
    ImageMagickColorMap["LightBlue3"] = "#9AC0CD"
    ImageMagickColorMap["DeepSkyBlue"] = "#00BFFF"
    ImageMagickColorMap["DeepSkyBlue1"] = "#00BFFF"
    ImageMagickColorMap["DeepSkyBlue2"] = "#00B2EE"
    ImageMagickColorMap["DeepSkyBlue4"] = "#00688B"
    ImageMagickColorMap["DeepSkyBlue3"] = "#009ACD"
    ImageMagickColorMap["LightBlue1"] = "#BFEFFF"
    ImageMagickColorMap["LightBlue2"] = "#B2DFEE"
    ImageMagickColorMap["LightBlue"] = "#ADD8E6"
    ImageMagickColorMap["LightBlue4"] = "#68838B"
    ImageMagickColorMap["PowderBlue"] = "#B0E0E6"
    ImageMagickColorMap["CadetBlue1"] = "#98F5FF"
    ImageMagickColorMap["CadetBlue2"] = "#8EE5EE"
    ImageMagickColorMap["CadetBlue3"] = "#7AC5CD"
    ImageMagickColorMap["CadetBlue4"] = "#53868B"
    ImageMagickColorMap["turquoise1"] = "#00F5FF"
    ImageMagickColorMap["turquoise2"] = "#00E5EE"
    ImageMagickColorMap["turquoise3"] = "#00C5CD"
    ImageMagickColorMap["turquoise4"] = "#00868B"
    ImageMagickColorMap["CadetBlue"] = "#5F9EA0"
    ImageMagickColorMap["DarkTurquoise"] = "#00CED1"
    ImageMagickColorMap["azure"] = "#F0FFFF"
    ImageMagickColorMap["azure1"] = "#F0FFFF"
    ImageMagickColorMap["LightCyan"] = "#E0FFFF"
    ImageMagickColorMap["LightCyan1"] = "#E0FFFF"
    ImageMagickColorMap["azure2"] = "#E0EEEE"
    ImageMagickColorMap["LightCyan2"] = "#D1EEEE"
    ImageMagickColorMap["PaleTurquoise1"] = "#BBFFFF"
    ImageMagickColorMap["PaleTurquoise"] = "#AFEEEE"
    ImageMagickColorMap["PaleTurquoise2"] = "#AEEEEE"
    ImageMagickColorMap["DarkSlateGray1"] = "#97FFFF"
    ImageMagickColorMap["azure3"] = "#C1CDCD"
    ImageMagickColorMap["LightCyan3"] = "#B4CDCD"
    ImageMagickColorMap["DarkSlateGray2"] = "#8DEEEE"
    ImageMagickColorMap["PaleTurquoise3"] = "#96CDCD"
    ImageMagickColorMap["DarkSlateGray3"] = "#79CDCD"
    ImageMagickColorMap["azure4"] = "#838B8B"
    ImageMagickColorMap["LightCyan4"] = "#7A8B8B"
    ImageMagickColorMap["aqua"] = "#00FFFF"
    ImageMagickColorMap["cyan"] = "#00FFFF"
    ImageMagickColorMap["cyan1"] = "#00FFFF"
    ImageMagickColorMap["PaleTurquoise4"] = "#668B8B"
    ImageMagickColorMap["cyan2"] = "#00EEEE"
    ImageMagickColorMap["DarkSlateGray4"] = "#528B8B"
    ImageMagickColorMap["cyan3"] = "#00CDCD"
    ImageMagickColorMap["cyan4"] = "#008B8B"
    ImageMagickColorMap["DarkCyan"] = "#008B8B"
    ImageMagickColorMap["teal"] = "#008080"
    ImageMagickColorMap["DarkSlateGray"] = "#2F4F4F"
    ImageMagickColorMap["DarkSlateGrey"] = "#2F4F4F"
    ImageMagickColorMap["MediumTurquoise"] = "#48D1CC"
    ImageMagickColorMap["LightSeaGreen"] = "#20B2AA"
    ImageMagickColorMap["turquoise"] = "#40E0D0"
    ImageMagickColorMap["aquamarine4"] = "#458B74"
    ImageMagickColorMap["aquamarine"] = "#7FFFD4"
    ImageMagickColorMap["aquamarine1"] = "#7FFFD4"
    ImageMagickColorMap["aquamarine2"] = "#76EEC6"
    ImageMagickColorMap["aquamarine3"] = "#66CDAA"
    ImageMagickColorMap["MediumAquamarine"] = "#66CDAA"
    ImageMagickColorMap["MediumSpringGreen"] = "#00FA9A"
    ImageMagickColorMap["MintCream"] = "#F5FFFA"
    ImageMagickColorMap["SpringGreen"] = "#00FF7F"
    ImageMagickColorMap["SpringGreen1"] = "#00FF7F"
    ImageMagickColorMap["SpringGreen2"] = "#00EE76"
    ImageMagickColorMap["SpringGreen3"] = "#00CD66"
    ImageMagickColorMap["SpringGreen4"] = "#008B45"
    ImageMagickColorMap["MediumSeaGreen"] = "#3CB371"
    ImageMagickColorMap["SeaGreen"] = "#2E8B57"
    ImageMagickColorMap["SeaGreen3"] = "#43CD80"
    ImageMagickColorMap["SeaGreen1"] = "#54FF9F"
    ImageMagickColorMap["SeaGreen4"] = "#2E8B57"
    ImageMagickColorMap["SeaGreen2"] = "#4EEE94"
    ImageMagickColorMap["MediumForestGreen"] = "#32814B"
    ImageMagickColorMap["honeydew"] = "#F0FFF0"
    ImageMagickColorMap["honeydew1"] = "#F0FFF0"
    ImageMagickColorMap["honeydew2"] = "#E0EEE0"
    ImageMagickColorMap["DarkSeaGreen1"] = "#C1FFC1"
    ImageMagickColorMap["DarkSeaGreen2"] = "#B4EEB4"
    ImageMagickColorMap["PaleGreen1"] = "#9AFF9A"
    ImageMagickColorMap["PaleGreen"] = "#98FB98"
    ImageMagickColorMap["honeydew3"] = "#C1CDC1"
    ImageMagickColorMap["LightGreen"] = "#90EE90"
    ImageMagickColorMap["PaleGreen2"] = "#90EE90"
    ImageMagickColorMap["DarkSeaGreen3"] = "#9BCD9B"
    ImageMagickColorMap["DarkSeaGreen"] = "#8FBC8F"
    ImageMagickColorMap["PaleGreen3"] = "#7CCD7C"
    ImageMagickColorMap["honeydew4"] = "#838B83"
    ImageMagickColorMap["green1"] = "#00FF00"
    ImageMagickColorMap["lime"] = "#00FF00"
    ImageMagickColorMap["LimeGreen"] = "#32CD32"
    ImageMagickColorMap["DarkSeaGreen4"] = "#698B69"
    ImageMagickColorMap["green2"] = "#00EE00"
    ImageMagickColorMap["PaleGreen4"] = "#548B54"
    ImageMagickColorMap["green3"] = "#00CD00"
    ImageMagickColorMap["ForestGreen"] = "#228B22"
    ImageMagickColorMap["green4"] = "#008B00"
    ImageMagickColorMap["green"] = "#008000"
    ImageMagickColorMap["DarkGreen"] = "#006400"
    ImageMagickColorMap["LawnGreen"] = "#7CFC00"
    ImageMagickColorMap["chartreuse"] = "#7FFF00"
    ImageMagickColorMap["chartreuse1"] = "#7FFF00"
    ImageMagickColorMap["chartreuse2"] = "#76EE00"
    ImageMagickColorMap["chartreuse3"] = "#66CD00"
    ImageMagickColorMap["chartreuse4"] = "#458B00"
    ImageMagickColorMap["GreenYellow"] = "#ADFF2F"
    ImageMagickColorMap["DarkOliveGreen3"] = "#A2CD5A"
    ImageMagickColorMap["DarkOliveGreen1"] = "#CAFF70"
    ImageMagickColorMap["DarkOliveGreen2"] = "#BCEE68"
    ImageMagickColorMap["DarkOliveGreen4"] = "#6E8B3D"
    ImageMagickColorMap["DarkOliveGreen"] = "#556B2F"
    ImageMagickColorMap["OliveDrab"] = "#6B8E23"
    ImageMagickColorMap["OliveDrab1"] = "#C0FF3E"
    ImageMagickColorMap["OliveDrab2"] = "#B3EE3A"
    ImageMagickColorMap["OliveDrab3"] = "#9ACD32"
    ImageMagickColorMap["YellowGreen"] = "#9ACD32"
    ImageMagickColorMap["OliveDrab4"] = "#698B22"
    ImageMagickColorMap["ivory"] = "#FFFFF0"
    ImageMagickColorMap["ivory1"] = "#FFFFF0"
    ImageMagickColorMap["LightYellow"] = "#FFFFE0"
    ImageMagickColorMap["LightYellow1"] = "#FFFFE0"
    ImageMagickColorMap["beige"] = "#F5F5DC"
    ImageMagickColorMap["ivory2"] = "#EEEEE0"
    ImageMagickColorMap["LightGoldenrodYellow"] = "#FAFAD2"
    ImageMagickColorMap["LightYellow2"] = "#EEEED1"
    ImageMagickColorMap["ivory3"] = "#CDCDC1"
    ImageMagickColorMap["LightYellow3"] = "#CDCDB4"
    ImageMagickColorMap["ivory4"] = "#8B8B83"
    ImageMagickColorMap["LightYellow4"] = "#8B8B7A"
    ImageMagickColorMap["yellow"] = "#FFFF00"
    ImageMagickColorMap["yellow1"] = "#FFFF00"
    ImageMagickColorMap["yellow2"] = "#EEEE00"
    ImageMagickColorMap["yellow3"] = "#CDCD00"
    ImageMagickColorMap["yellow4"] = "#8B8B00"
    ImageMagickColorMap["olive"] = "#808000"
    ImageMagickColorMap["DarkKhaki"] = "#BDB76B"
    ImageMagickColorMap["khaki2"] = "#EEE685"
    ImageMagickColorMap["LemonChiffon4"] = "#8B8970"
    ImageMagickColorMap["khaki1"] = "#FFF68F"
    ImageMagickColorMap["khaki3"] = "#CDC673"
    ImageMagickColorMap["khaki4"] = "#8B864E"
    ImageMagickColorMap["PaleGoldenrod"] = "#EEE8AA"
    ImageMagickColorMap["LemonChiffon"] = "#FFFACD"
    ImageMagickColorMap["LemonChiffon1"] = "#FFFACD"
    ImageMagickColorMap["khaki"] = "#F0E68C"
    ImageMagickColorMap["LemonChiffon3"] = "#CDC9A5"
    ImageMagickColorMap["LemonChiffon2"] = "#EEE9BF"
    ImageMagickColorMap["MediumGoldenRod"] = "#D1C166"
    ImageMagickColorMap["cornsilk4"] = "#8B8878"
    ImageMagickColorMap["gold"] = "#FFD700"
    ImageMagickColorMap["gold1"] = "#FFD700"
    ImageMagickColorMap["gold2"] = "#EEC900"
    ImageMagickColorMap["gold3"] = "#CDAD00"
    ImageMagickColorMap["gold4"] = "#8B7500"
    ImageMagickColorMap["LightGoldenrod"] = "#EEDD82"
    ImageMagickColorMap["LightGoldenrod4"] = "#8B814C"
    ImageMagickColorMap["LightGoldenrod1"] = "#FFEC8B"
    ImageMagickColorMap["LightGoldenrod3"] = "#CDBE70"
    ImageMagickColorMap["LightGoldenrod2"] = "#EEDC82"
    ImageMagickColorMap["cornsilk3"] = "#CDC8B1"
    ImageMagickColorMap["cornsilk2"] = "#EEE8CD"
    ImageMagickColorMap["cornsilk"] = "#FFF8DC"
    ImageMagickColorMap["cornsilk1"] = "#FFF8DC"
    ImageMagickColorMap["goldenrod"] = "#DAA520"
    ImageMagickColorMap["goldenrod1"] = "#FFC125"
    ImageMagickColorMap["goldenrod2"] = "#EEB422"
    ImageMagickColorMap["goldenrod3"] = "#CD9B1D"
    ImageMagickColorMap["goldenrod4"] = "#8B6914"
    ImageMagickColorMap["DarkGoldenrod"] = "#B8860B"
    ImageMagickColorMap["DarkGoldenrod1"] = "#FFB90F"
    ImageMagickColorMap["DarkGoldenrod2"] = "#EEAD0E"
    ImageMagickColorMap["DarkGoldenrod3"] = "#CD950C"
    ImageMagickColorMap["DarkGoldenrod4"] = "#8B6508"
    ImageMagickColorMap["FloralWhite"] = "#FFFAF0"
    ImageMagickColorMap["wheat2"] = "#EED8AE"
    ImageMagickColorMap["OldLace"] = "#FDF5E6"
    ImageMagickColorMap["wheat"] = "#F5DEB3"
    ImageMagickColorMap["wheat1"] = "#FFE7BA"
    ImageMagickColorMap["wheat3"] = "#CDBA96"
    ImageMagickColorMap["orange"] = "#FFA500"
    ImageMagickColorMap["orange1"] = "#FFA500"
    ImageMagickColorMap["orange2"] = "#EE9A00"
    ImageMagickColorMap["orange3"] = "#CD8500"
    ImageMagickColorMap["orange4"] = "#8B5A00"
    ImageMagickColorMap["wheat4"] = "#8B7E66"
    ImageMagickColorMap["moccasin"] = "#FFE4B5"
    ImageMagickColorMap["PapayaWhip"] = "#FFEFD5"
    ImageMagickColorMap["NavajoWhite3"] = "#CDB38B"
    ImageMagickColorMap["BlanchedAlmond"] = "#FFEBCD"
    ImageMagickColorMap["NavajoWhite"] = "#FFDEAD"
    ImageMagickColorMap["NavajoWhite1"] = "#FFDEAD"
    ImageMagickColorMap["NavajoWhite2"] = "#EECFA1"
    ImageMagickColorMap["NavajoWhite4"] = "#8B795E"
    ImageMagickColorMap["AntiqueWhite4"] = "#8B8378"
    ImageMagickColorMap["AntiqueWhite"] = "#FAEBD7"
    ImageMagickColorMap["tan"] = "#D2B48C"
    ImageMagickColorMap["bisque4"] = "#8B7D6B"
    ImageMagickColorMap["burlywood"] = "#DEB887"
    ImageMagickColorMap["AntiqueWhite2"] = "#EEDFCC"
    ImageMagickColorMap["burlywood1"] = "#FFD39B"
    ImageMagickColorMap["burlywood3"] = "#CDAA7D"
    ImageMagickColorMap["burlywood2"] = "#EEC591"
    ImageMagickColorMap["AntiqueWhite1"] = "#FFEFDB"
    ImageMagickColorMap["burlywood4"] = "#8B7355"
    ImageMagickColorMap["AntiqueWhite3"] = "#CDC0B0"
    ImageMagickColorMap["DarkOrange"] = "#FF8C00"
    ImageMagickColorMap["bisque2"] = "#EED5B7"
    ImageMagickColorMap["bisque"] = "#FFE4C4"
    ImageMagickColorMap["bisque1"] = "#FFE4C4"
    ImageMagickColorMap["bisque3"] = "#CDB79E"
    ImageMagickColorMap["DarkOrange1"] = "#FF7F00"
    ImageMagickColorMap["linen"] = "#FAF0E6"
    ImageMagickColorMap["DarkOrange2"] = "#EE7600"
    ImageMagickColorMap["DarkOrange3"] = "#CD6600"
    ImageMagickColorMap["DarkOrange4"] = "#8B4500"
    ImageMagickColorMap["peru"] = "#CD853F"
    ImageMagickColorMap["tan1"] = "#FFA54F"
    ImageMagickColorMap["tan2"] = "#EE9A49"
    ImageMagickColorMap["tan3"] = "#CD853F"
    ImageMagickColorMap["tan4"] = "#8B5A2B"
    ImageMagickColorMap["PeachPuff"] = "#FFDAB9"
    ImageMagickColorMap["PeachPuff1"] = "#FFDAB9"
    ImageMagickColorMap["PeachPuff4"] = "#8B7765"
    ImageMagickColorMap["PeachPuff2"] = "#EECBAD"
    ImageMagickColorMap["PeachPuff3"] = "#CDAF95"
    ImageMagickColorMap["SandyBrown"] = "#F4A460"
    ImageMagickColorMap["seashell4"] = "#8B8682"
    ImageMagickColorMap["seashell2"] = "#EEE5DE"
    ImageMagickColorMap["seashell3"] = "#CDC5BF"
    ImageMagickColorMap["chocolate"] = "#D2691E"
    ImageMagickColorMap["chocolate1"] = "#FF7F24"
    ImageMagickColorMap["chocolate2"] = "#EE7621"
    ImageMagickColorMap["chocolate3"] = "#CD661D"
    ImageMagickColorMap["chocolate4"] = "#8B4513"
    ImageMagickColorMap["SaddleBrown"] = "#8B4513"
    ImageMagickColorMap["seashell"] = "#FFF5EE"
    ImageMagickColorMap["seashell1"] = "#FFF5EE"
    ImageMagickColorMap["sienna4"] = "#8B4726"
    ImageMagickColorMap["sienna"] = "#A0522D"
    ImageMagickColorMap["sienna1"] = "#FF8247"
    ImageMagickColorMap["sienna2"] = "#EE7942"
    ImageMagickColorMap["sienna3"] = "#CD6839"
    ImageMagickColorMap["LightSalmon3"] = "#CD8162"
    ImageMagickColorMap["LightSalmon"] = "#FFA07A"
    ImageMagickColorMap["LightSalmon1"] = "#FFA07A"
    ImageMagickColorMap["LightSalmon4"] = "#8B5742"
    ImageMagickColorMap["LightSalmon2"] = "#EE9572"
    ImageMagickColorMap["coral"] = "#FF7F50"
    ImageMagickColorMap["OrangeRed"] = "#FF4500"
    ImageMagickColorMap["OrangeRed1"] = "#FF4500"
    ImageMagickColorMap["OrangeRed2"] = "#EE4000"
    ImageMagickColorMap["OrangeRed3"] = "#CD3700"
    ImageMagickColorMap["OrangeRed4"] = "#8B2500"
    ImageMagickColorMap["DarkSalmon"] = "#E9967A"
    ImageMagickColorMap["salmon1"] = "#FF8C69"
    ImageMagickColorMap["salmon2"] = "#EE8262"
    ImageMagickColorMap["salmon3"] = "#CD7054"
    ImageMagickColorMap["salmon4"] = "#8B4C39"
    ImageMagickColorMap["coral1"] = "#FF7256"
    ImageMagickColorMap["coral2"] = "#EE6A50"
    ImageMagickColorMap["coral3"] = "#CD5B45"
    ImageMagickColorMap["coral4"] = "#8B3E2F"
    ImageMagickColorMap["tomato4"] = "#8B3626"
    ImageMagickColorMap["tomato"] = "#FF6347"
    ImageMagickColorMap["tomato1"] = "#FF6347"
    ImageMagickColorMap["tomato2"] = "#EE5C42"
    ImageMagickColorMap["tomato3"] = "#CD4F39"
    ImageMagickColorMap["MistyRose4"] = "#8B7D7B"
    ImageMagickColorMap["MistyRose2"] = "#EED5D2"
    ImageMagickColorMap["MistyRose"] = "#FFE4E1"
    ImageMagickColorMap["MistyRose1"] = "#FFE4E1"
    ImageMagickColorMap["salmon"] = "#FA8072"
    ImageMagickColorMap["MistyRose3"] = "#CDB7B5"
    ImageMagickColorMap["white"] = "#FFFFFF"
    ImageMagickColorMap["gray100"] = "#FFFFFF"
    ImageMagickColorMap["grey100"] = "#FFFFFF"
    ImageMagickColorMap["grey100"] = "#FFFFFF"
    ImageMagickColorMap["gray99"] = "#FCFCFC"
    ImageMagickColorMap["grey99"] = "#FCFCFC"
    ImageMagickColorMap["gray98"] = "#FAFAFA"
    ImageMagickColorMap["grey98"] = "#FAFAFA"
    ImageMagickColorMap["gray97"] = "#F7F7F7"
    ImageMagickColorMap["grey97"] = "#F7F7F7"
    ImageMagickColorMap["gray96"] = "#F5F5F5"
    ImageMagickColorMap["grey96"] = "#F5F5F5"
    ImageMagickColorMap["WhiteSmoke"] = "#F5F5F5"
    ImageMagickColorMap["gray95"] = "#F2F2F2"
    ImageMagickColorMap["grey95"] = "#F2F2F2"
    ImageMagickColorMap["gray94"] = "#F0F0F0"
    ImageMagickColorMap["grey94"] = "#F0F0F0"
    ImageMagickColorMap["gray93"] = "#EDEDED"
    ImageMagickColorMap["grey93"] = "#EDEDED"
    ImageMagickColorMap["gray92"] = "#EBEBEB"
    ImageMagickColorMap["grey92"] = "#EBEBEB"
    ImageMagickColorMap["gray91"] = "#E8E8E8"
    ImageMagickColorMap["grey91"] = "#E8E8E8"
    ImageMagickColorMap["gray90"] = "#E5E5E5"
    ImageMagickColorMap["grey90"] = "#E5E5E5"
    ImageMagickColorMap["gray89"] = "#E3E3E3"
    ImageMagickColorMap["grey89"] = "#E3E3E3"
    ImageMagickColorMap["gray88"] = "#E0E0E0"
    ImageMagickColorMap["grey88"] = "#E0E0E0"
    ImageMagickColorMap["gray87"] = "#DEDEDE"
    ImageMagickColorMap["grey87"] = "#DEDEDE"
    ImageMagickColorMap["gainsboro"] = "#DCDCDC"
    ImageMagickColorMap["gray86"] = "#DBDBDB"
    ImageMagickColorMap["grey86"] = "#DBDBDB"
    ImageMagickColorMap["gray85"] = "#D9D9D9"
    ImageMagickColorMap["grey85"] = "#D9D9D9"
    ImageMagickColorMap["gray84"] = "#D6D6D6"
    ImageMagickColorMap["grey84"] = "#D6D6D6"
    ImageMagickColorMap["gray83"] = "#D4D4D4"
    ImageMagickColorMap["grey83"] = "#D4D4D4"
    ImageMagickColorMap["LightGray"] = "#D3D3D3"
    ImageMagickColorMap["LightGrey"] = "#D3D3D3"
    ImageMagickColorMap["gray82"] = "#D1D1D1"
    ImageMagickColorMap["grey82"] = "#D1D1D1"
    ImageMagickColorMap["gray81"] = "#CFCFCF"
    ImageMagickColorMap["grey81"] = "#CFCFCF"
    ImageMagickColorMap["gray80"] = "#CCCCCC"
    ImageMagickColorMap["grey80"] = "#CCCCCC"
    ImageMagickColorMap["gray79"] = "#C9C9C9"
    ImageMagickColorMap["grey79"] = "#C9C9C9"
    ImageMagickColorMap["gray78"] = "#C7C7C7"
    ImageMagickColorMap["grey78"] = "#C7C7C7"
    ImageMagickColorMap["gray77"] = "#C4C4C4"
    ImageMagickColorMap["grey77"] = "#C4C4C4"
    ImageMagickColorMap["gray76"] = "#C2C2C2"
    ImageMagickColorMap["grey76"] = "#C2C2C2"
    ImageMagickColorMap["silver"] = "#C0C0C0"
    ImageMagickColorMap["gray75"] = "#BFBFBF"
    ImageMagickColorMap["grey75"] = "#BFBFBF"
    ImageMagickColorMap["gray74"] = "#BDBDBD"
    ImageMagickColorMap["grey74"] = "#BDBDBD"
    ImageMagickColorMap["gray73"] = "#BABABA"
    ImageMagickColorMap["grey73"] = "#BABABA"
    ImageMagickColorMap["gray72"] = "#B8B8B8"
    ImageMagickColorMap["grey72"] = "#B8B8B8"
    ImageMagickColorMap["gray71"] = "#B5B5B5"
    ImageMagickColorMap["grey71"] = "#B5B5B5"
    ImageMagickColorMap["gray70"] = "#B3B3B3"
    ImageMagickColorMap["grey70"] = "#B3B3B3"
    ImageMagickColorMap["gray69"] = "#B0B0B0"
    ImageMagickColorMap["grey69"] = "#B0B0B0"
    ImageMagickColorMap["gray68"] = "#ADADAD"
    ImageMagickColorMap["grey68"] = "#ADADAD"
    ImageMagickColorMap["gray67"] = "#ABABAB"
    ImageMagickColorMap["grey67"] = "#ABABAB"
    ImageMagickColorMap["DarkGray"] = "#A9A9A9"
    ImageMagickColorMap["DarkGrey"] = "#A9A9A9"
    ImageMagickColorMap["gray66"] = "#A8A8A8"
    ImageMagickColorMap["grey66"] = "#A8A8A8"
    ImageMagickColorMap["gray65"] = "#A6A6A6"
    ImageMagickColorMap["grey65"] = "#A6A6A6"
    ImageMagickColorMap["gray64"] = "#A3A3A3"
    ImageMagickColorMap["grey64"] = "#A3A3A3"
    ImageMagickColorMap["gray63"] = "#A1A1A1"
    ImageMagickColorMap["grey63"] = "#A1A1A1"
    ImageMagickColorMap["gray62"] = "#9E9E9E"
    ImageMagickColorMap["grey62"] = "#9E9E9E"
    ImageMagickColorMap["gray61"] = "#9C9C9C"
    ImageMagickColorMap["grey61"] = "#9C9C9C"
    ImageMagickColorMap["gray60"] = "#999999"
    ImageMagickColorMap["grey60"] = "#999999"
    ImageMagickColorMap["gray59"] = "#969696"
    ImageMagickColorMap["grey59"] = "#969696"
    ImageMagickColorMap["gray58"] = "#949494"
    ImageMagickColorMap["grey58"] = "#949494"
    ImageMagickColorMap["gray57"] = "#919191"
    ImageMagickColorMap["grey57"] = "#919191"
    ImageMagickColorMap["gray56"] = "#8F8F8F"
    ImageMagickColorMap["grey56"] = "#8F8F8F"
    ImageMagickColorMap["gray55"] = "#8C8C8C"
    ImageMagickColorMap["grey55"] = "#8C8C8C"
    ImageMagickColorMap["gray54"] = "#8A8A8A"
    ImageMagickColorMap["grey54"] = "#8A8A8A"
    ImageMagickColorMap["gray53"] = "#878787"
    ImageMagickColorMap["grey53"] = "#878787"
    ImageMagickColorMap["gray52"] = "#858585"
    ImageMagickColorMap["grey52"] = "#858585"
    ImageMagickColorMap["gray51"] = "#828282"
    ImageMagickColorMap["grey51"] = "#828282"
    ImageMagickColorMap["fractal"] = "#808080"
    ImageMagickColorMap["gray50"] = "#7F7F7F"
    ImageMagickColorMap["grey50"] = "#7F7F7F"
    ImageMagickColorMap["gray"] = "#7E7E7E"
    ImageMagickColorMap["gray49"] = "#7D7D7D"
    ImageMagickColorMap["grey49"] = "#7D7D7D"
    ImageMagickColorMap["gray48"] = "#7A7A7A"
    ImageMagickColorMap["grey48"] = "#7A7A7A"
    ImageMagickColorMap["gray47"] = "#787878"
    ImageMagickColorMap["grey47"] = "#787878"
    ImageMagickColorMap["gray46"] = "#757575"
    ImageMagickColorMap["grey46"] = "#757575"
    ImageMagickColorMap["gray45"] = "#737373"
    ImageMagickColorMap["grey45"] = "#737373"
    ImageMagickColorMap["gray44"] = "#707070"
    ImageMagickColorMap["grey44"] = "#707070"
    ImageMagickColorMap["gray43"] = "#6E6E6E"
    ImageMagickColorMap["grey43"] = "#6E6E6E"
    ImageMagickColorMap["gray42"] = "#6B6B6B"
    ImageMagickColorMap["grey42"] = "#6B6B6B"
    ImageMagickColorMap["DimGray"] = "#696969"
    ImageMagickColorMap["DimGrey"] = "#696969"
    ImageMagickColorMap["gray41"] = "#696969"
    ImageMagickColorMap["grey41"] = "#696969"
    ImageMagickColorMap["gray40"] = "#666666"
    ImageMagickColorMap["grey40"] = "#666666"
    ImageMagickColorMap["gray39"] = "#636363"
    ImageMagickColorMap["grey39"] = "#636363"
    ImageMagickColorMap["gray38"] = "#616161"
    ImageMagickColorMap["grey38"] = "#616161"
    ImageMagickColorMap["gray37"] = "#5E5E5E"
    ImageMagickColorMap["grey37"] = "#5E5E5E"
    ImageMagickColorMap["gray36"] = "#5C5C5C"
    ImageMagickColorMap["grey36"] = "#5C5C5C"
    ImageMagickColorMap["gray35"] = "#595959"
    ImageMagickColorMap["grey35"] = "#595959"
    ImageMagickColorMap["gray34"] = "#575757"
    ImageMagickColorMap["grey34"] = "#575757"
    ImageMagickColorMap["gray33"] = "#545454"
    ImageMagickColorMap["grey33"] = "#545454"
    ImageMagickColorMap["gray32"] = "#525252"
    ImageMagickColorMap["grey32"] = "#525252"
    ImageMagickColorMap["gray31"] = "#4F4F4F"
    ImageMagickColorMap["grey31"] = "#4F4F4F"
    ImageMagickColorMap["gray30"] = "#4D4D4D"
    ImageMagickColorMap["grey30"] = "#4D4D4D"
    ImageMagickColorMap["gray29"] = "#4A4A4A"
    ImageMagickColorMap["grey29"] = "#4A4A4A"
    ImageMagickColorMap["gray28"] = "#474747"
    ImageMagickColorMap["grey28"] = "#474747"
    ImageMagickColorMap["gray27"] = "#454545"
    ImageMagickColorMap["grey27"] = "#454545"
    ImageMagickColorMap["gray26"] = "#424242"
    ImageMagickColorMap["grey26"] = "#424242"
    ImageMagickColorMap["gray25"] = "#404040"
    ImageMagickColorMap["grey25"] = "#404040"
    ImageMagickColorMap["gray24"] = "#3D3D3D"
    ImageMagickColorMap["grey24"] = "#3D3D3D"
    ImageMagickColorMap["gray23"] = "#3B3B3B"
    ImageMagickColorMap["grey23"] = "#3B3B3B"
    ImageMagickColorMap["gray22"] = "#383838"
    ImageMagickColorMap["grey22"] = "#383838"
    ImageMagickColorMap["gray21"] = "#363636"
    ImageMagickColorMap["grey21"] = "#363636"
    ImageMagickColorMap["gray20"] = "#333333"
    ImageMagickColorMap["grey20"] = "#333333"
    ImageMagickColorMap["gray19"] = "#303030"
    ImageMagickColorMap["grey19"] = "#303030"
    ImageMagickColorMap["gray18"] = "#2E2E2E"
    ImageMagickColorMap["grey18"] = "#2E2E2E"
    ImageMagickColorMap["gray17"] = "#2B2B2B"
    ImageMagickColorMap["grey17"] = "#2B2B2B"
    ImageMagickColorMap["gray16"] = "#292929"
    ImageMagickColorMap["grey16"] = "#292929"
    ImageMagickColorMap["gray15"] = "#262626"
    ImageMagickColorMap["grey15"] = "#262626"
    ImageMagickColorMap["gray14"] = "#242424"
    ImageMagickColorMap["grey14"] = "#242424"
    ImageMagickColorMap["gray13"] = "#212121"
    ImageMagickColorMap["grey13"] = "#212121"
    ImageMagickColorMap["gray12"] = "#1F1F1F"
    ImageMagickColorMap["grey12"] = "#1F1F1F"
    ImageMagickColorMap["gray11"] = "#1C1C1C"
    ImageMagickColorMap["grey11"] = "#1C1C1C"
    ImageMagickColorMap["gray10"] = "#1A1A1A"
    ImageMagickColorMap["grey10"] = "#1A1A1A"
    ImageMagickColorMap["gray9"] = "#171717"
    ImageMagickColorMap["grey9"] = "#171717"
    ImageMagickColorMap["gray8"] = "#141414"
    ImageMagickColorMap["grey8"] = "#141414"
    ImageMagickColorMap["gray7"] = "#121212"
    ImageMagickColorMap["grey7"] = "#121212"
    ImageMagickColorMap["gray6"] = "#0F0F0F"
    ImageMagickColorMap["grey6"] = "#0F0F0F"
    ImageMagickColorMap["gray5"] = "#0D0D0D"
    ImageMagickColorMap["grey5"] = "#0D0D0D"
    ImageMagickColorMap["gray4"] = "#0A0A0A"
    ImageMagickColorMap["grey4"] = "#0A0A0A"
    ImageMagickColorMap["gray3"] = "#080808"
    ImageMagickColorMap["grey3"] = "#080808"
    ImageMagickColorMap["gray2"] = "#050505"
    ImageMagickColorMap["grey2"] = "#050505"
    ImageMagickColorMap["gray1"] = "#030303"
    ImageMagickColorMap["grey1"] = "#030303"
    ImageMagickColorMap["black"] = "#000000"
    ImageMagickColorMap["gray0"] = "#000000"
    ImageMagickColorMap["grey0"] = "#000000"
    ImageMagickColorMap["opaque"] = "#000000"
    
    @staticmethod
    def rgbFromStr(s):  
        # s starts with a #.  
        r, g, b = int(s[1:3],16), int(s[3:5], 16),int(s[5:7], 16)  
        return r, g, b  
    
    @staticmethod
    def findNearestWebColorName((R,G,B)):  
        return ColorNames.findNearestColorName((R,G,B),ColorNames.WebColorMap)
    
    @staticmethod
    def findNearestImageMagickColorName((R,G,B)):  
        return ColorNames.findNearestColorName((R,G,B),ColorNames.ImageMagickColorMap)
    
    @staticmethod
    def findNearestColorName((R,G,B),Map):  
        mindiff = None
        for d in Map:  
            r, g, b = ColorNames.rgbFromStr(Map[d])  
            diff = abs(R -r)*256 + abs(G-g)* 256 + abs(B- b)* 256   
            if mindiff is None or diff < mindiff:  
                mindiff = diff  
                mincolorname = d  
        return mincolorname
        
class VideoWriter():
    '''
    Class to write frames using ffmpeg
    '''
    
    def __init__(self,xsize=480,ysize=640,FPS=29,outFile="temp.mp4",quality=25,show_output='quiet', FFMPEG_BINARY='ffmpeg'):
        self.outFile = outFile
        self.xsize,self.ysize,self.FPS = xsize,ysize,FPS
        self.show_output = show_output
        self.quality = quality
        self.FFMPEG_BIN = FFMPEG_BINARY

        self.buildWriter()

    def buildWriter(self):
        '''
        explanation of complicated ffmpeg string:
        -y              : overwrite existing file
        -framerate      : input framerate (nominally 1, but override with timelapse framerate)
        -f              : input format - as we are sending raw yuv420p frames, use rawvideo
        -vcodec         : just rawvideo
        -s              : frame size (note 480x640 as we rotate the frame)
        -pic_fmt        : as we said we are sending yuv420p pixels so define it here
        -i              : - input from stdin (in our case a pipe)
        -crf            : h264 (x264) quality
        -an             : no audio
        -movflags isml+frag_keyframe+separate_moof  : To make live Smooth Streaming (ISML) from real time input.
                                                      mp4 output has a moov atom at the end. If the video gets interrupted and this is not written, the file is corrupted.
                                                      these options cause the mp4 to be written as a fragmented mp4.
                                                      A fragmented mp4 file is internally divided into several back-to-back chunks or MPEG-4 movie fragments. 
                                                      Each chunk has its own moof atom - so there are several moof atoms interleaved in the file instead of a single moov at the end
                                                      as in the case of an unfragmented mp4. This makes it easier to stream over slow networks where buffering is involved,
                                                      and viewable in case of interruptions.
                                                      NOTE Quicktime may not like this.
        -frag_duration  : point (in seconds) at which the moof atoms are written, so at a frame rate of 10x, and set to 3, a moof atom would be written every 30 frames.
        -value          : verbose level, leave at -8(quiet) for no output. normal is 'info' which produces a lot of output.
        output filename : extension determines the codec used for conversion, in our case .mp4 is probably best.
        '''
        commandWriter = [   self.FFMPEG_BIN,
                            '-y',
                            '-framerate', str(self.FPS),
                            '-f', 'rawvideo',
                            '-vcodec', 'rawvideo',
                            '-s', '%dx%d' % (self.xsize, self.ysize),
                            '-pix_fmt', 'yuv420p',
                            '-i', '-',
                            '-crf', str(self.quality), 
                            '-an',
                            '-movflags', 'isml+frag_keyframe+separate_moof',
                            '-frag_duration',  '3', 
                            '-v', self.show_output,
                            self.outFile ]
        log.debug("ffmpeg command: %s" % " ".join(commandWriter))
        self.pW = subprocess.Popen(commandWriter,stdin = subprocess.PIPE, bufsize=0)

    def write(self,frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
        self.pW.stdin.write(img.tostring())
        self.pW.stdin.flush()

    def release(self):
        self.pW.stdin.flush()
        self.pW.communicate()
        self.pW.stdin.close()
       
#----------------------End of Classes -------------------------

#setup logging
def setup_logger(logger_name, log_file, level=None, console=False):
    '''
    Set up logging system, log file has to be a list of files (can be a list of one),
    the first gets the console output.
    '''
    
    if not level:
        level = logging.DEBUG
    
    try:
        l = logging.getLogger(logger_name)
        formatter = logging.Formatter('[%(levelname)1.1s %(asctime)s %(threadName)10.10s] %(message)s')
        for i, file_name in enumerate(log_file):
            if file_name.upper() != 'NONE':
                fileHandler1 = logging.handlers.RotatingFileHandler(file_name, mode='a', maxBytes=2000000, backupCount=5)
                fileHandler1.setFormatter(formatter)
                fileHandler1.setLevel(level)
                l.addHandler(fileHandler1)
            if console == True and i == 0:
                streamHandler1 = logging.StreamHandler()
                l.addHandler(streamHandler1)               
            
        l.setLevel(level)
            
        
    except Exception as e:
        print("Error in Logging setup: %s - do you have write permission for the log file?" % e)
        sys.exit(1)
        
# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    if iteration > total:
        iteration = total
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█'.decode('utf8') * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    #if iteration == total:
    #    sys.stdout.write('\n')
    sys.stdout.flush()
        
        
def read_data(url):
    try:
        resp = urllib2.urlopen(url, timeout=3)
    except (urllib2.URLError, socket.timeout) as e:
        log.warn("read_data: There was an error: %r" % e)
        return None
    return resp.read()
    
def get_data(url):
    '''
    parses data url (/cgi-bin/config_periodic_data.cgi)
    set_status(Estimatetime, PrintJobStatus, PrintJobprocessing, filamentRemain, filamentSub, R, G, B, Material, bedTemp, NozzleTemp, FileName)
    set_status(1313, 10004,100, 44,44, 'ff', 'ff', 'ff',1,51,36,'reg_litho_3cm[766]'); 
    after boot, model name is empty:
    set_status(0, 9999,9999, 36,36, 'ff', 'ff', 'ff',1,41,51,'');
    
    Material == 1 // PLA
    Material == 2 // ABS
    Material == 3 // ABS (WOOD)
    Material == 4 // ABS (HIPS)
    Material == 5 // ABS (PETG)
    '''
    material_names={1:"PLA", 2:"ABS",3:"ABS(WOOD)",4:"ABS(HIPS)",5:"ABS(PETG)"}
    print_data = {'cloud_print': False}
    
    info = read_data(url)
    
    if info is None:
        info = "set_status(0, 9999, 9999, 100, 100, 'ff', 'ff', 'ff',1,0,0,'None');"
    info = info.replace("set_status(","").replace("'","").replace(";","").replace(")","").replace(" ","")
    #log.debug("info: %s" % repr(info))
    data_split = info.split(",")
    try:
        model_name = data_split[11]
    except IndexError:
        #handle missing model_name after boot
        model_name = 'None'
    if model_name=="gcodefile.gcode":
        print_data['cloud_print']       = True
    print_data['model_name']            = model_name 
    print_data['nozzel_temp']           = int(data_split[10])       #degrees C or F
    print_data['bed_temp']              = int(data_split[9])        #degrees C or F
    print_data['material']              = int(data_split[8])
    print_data['material_name']         = material_names.get(print_data['material'], "Unknown")
    print_data['material_color']        = "#%s%s%s" % (data_split[5],data_split[6],data_split[7])    #RGB colour
    print_data['material_color_name']   = ColorNames.findNearestWebColorName(ColorNames.rgbFromStr(print_data['material_color']))
    print_data['percent']               = int(data_split[2])        # %job remaining
    print_data['PrintJobStatus']        = int(data_split[1])        # 9999=undefined system loading.., 10001,10006=busy, 10004,10006,10007,10028=idle, 10002,10003,10018,10023,10021=printing
    print_data['Estimatetime']          = int(data_split[0])        # in seconds
    remain_time = print_data['Estimatetime']*(1- print_data['percent']*0.01)
    remain_time = remain_time/60                                    # total mins
    print_data['hours']                 = int(remain_time/60)       # hours
    print_data['mins']                  = int(remain_time%60)       # mins
    print_data['filamentRemain']        = int(data_split[3])        # % filament remaining
    print_data['filamentSub']           = int(data_split[4])        # % remain of second filament?
    return print_data
 
def get_printer_status(url):
    print_data = get_data(url)
    return print_data['PrintJobStatus']
    
def get_mode(mode, modes):
    text_modes = modes.keys()
    for text in text_modes:
        if mode in modes[text]:
            return text
    return "unknown"
        
def url_to_image(url):
    '''
    download the image, convert it to a NumPy array, and then read
    it into OpenCV format
    '''
    image = None
    raw_image = read_data(url)
    if raw_image is None:
        image = blank_img()
    else:
        img = np.asarray(bytearray(raw_image), dtype="uint8")
        image = cv2.imdecode(img, cv2.IMREAD_COLOR)
    
    if image is None:
        image = blank_img()

    return image
    
def url_to_image_generator(url):
    '''
    should get jpg from url, but not working
    '''
    cap = cv2.VideoCapture(url)
    cap.set(cv.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT,480)
    while True:
        if cap.isOpened():
            ret,img = cap.read()
            if not ret:
                log.warn("did not read frame")
                img = blank_img(480,640)
            yield img
        else:
            log.warn("Cap is not open")
            cap.open()
            #yield blank_img(480,640)
        
def rotate_img_crop(img, angle):
    '''
    Rotate image, but crop to original size
    '''
    num_rows, num_cols = img.shape[:2]

    rotation_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), angle, 1)
    img_rotation = cv2.warpAffine(img, rotation_matrix, (num_cols, num_rows))
    return img_rotation
    
def rotate_img(mat, angle):
    '''
    Rotate image and resize to fit bounds
    angle in degrees
    '''

    height, width = mat.shape[:2]
    image_center = (width/2, height/2)

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    abs_cos = abs(rotation_mat[0,0])
    abs_sin = abs(rotation_mat[0,1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat
    
def mse(imageA, imageB):
    '''
    the 'Mean Squared Error' between the two images is the
    sum of the squared difference between the two images;
    NOTE: the two images must have the same dimension
    '''
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
	
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err
    
def blank_img(height=640, width=480):
    img = np.zeros((height,width,3), np.uint8)
    return img
    
def overlay_image_alpha(img, img_overlay, pos, alpha_mask):
    '''
    Overlay img_overlay on top of img at the position specified by
    pos and blend using alpha_mask.

    Alpha mask must contain values within the range [0, 1] and be the
    same size as img_overlay.
    '''

    x, y = pos

    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    channels = img.shape[2]

    alpha = alpha_mask[y1o:y2o, x1o:x2o]
    alpha_inv = 1.0 - alpha

    for c in range(channels):
        img[y1:y2, x1:x2, c] = (alpha * img_overlay[y1o:y2o, x1o:x2o, c] + alpha_inv * img[y1:y2, x1:x2, c])
    return img
    
def overlay_text(img, out_file, started, PrintJobStatus, fps, print_data, duration, modes, opacity, extra_text=True):
    '''
    Modifies copy of image, does not touch original
    returns copy
    '''
    overlay_text = img.copy()
    elapsed_time = datetime.timedelta(seconds=int(time.time()-started))
    startime = datetime.datetime.fromtimestamp(started).replace(microsecond=0)
    duration = datetime.timedelta(seconds=duration)
    initial_txt = '\n3DWOX Timelapse V%s\n%s\n%s' % (__version__,out_file,startime)
    if not extra_text: #remove extraneous text after x(30) seconds
        initial_txt = ''
    footer1 = "mode:%d(%s)\nbed T:%d noz T:%d\nFil: %s,%s %d%%\nFPS: %dx, dur: %s%s"  % (   PrintJobStatus,
                                                                                            get_mode(PrintJobStatus, modes),
                                                                                            print_data['bed_temp'],
                                                                                            print_data['nozzel_temp'],
                                                                                            print_data['material_color_name'],
                                                                                            print_data['material_name'],
                                                                                            print_data['filamentRemain'],
                                                                                            fps,
                                                                                            duration,
                                                                                            initial_txt)

    footer = "%-12.12s Time %.2d:%.2d %3d%% %s" % ( print_data['model_name'] if len(print_data['model_name']) < 12 else print_data['model_name'][:10]+"..",
                                                    print_data['hours'],
                                                    print_data['mins'],
                                                    print_data['percent'],
                                                    elapsed_time)
    box1, _ = cv2.getTextSize(footer1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    box, _  = cv2.getTextSize(footer, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
    for i, line in enumerate(reversed(footer1.split('\n'))):
        cv2.putText(overlay_text, line, (0,640-box[1]*2-i*(box1[1]+3)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0),1)   #black text
    cv2.putText(overlay_text, footer, (0,640-box[1]/2), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255),2)            #white text
    cv2.addWeighted(overlay_text, opacity, overlay_text, 1 - opacity, 0, overlay_text)
    return overlay_text
    
def get_filename(out_file, extension=None, out_dir=None):
    '''
    get unique file name, change extension if given
    '''
    
    dst_dir, basename = os.path.split(out_file)
    if out_dir is not None:
        dst_dir = out_dir
    head, tail = os.path.splitext(basename)
    if extension is not None:
        tail = extension
    if tail == '':
        tail='.avi'
    out_file = os.path.join(dst_dir, '%s%s' % (head, tail))
    if os.path.exists(out_file):    #don't overwrite existing files
        count = 0
        dst_dir, basename = os.path.split(out_file)
        head, tail = os.path.splitext(basename)
        while os.path.exists(out_file):
            count += 1
            out_file = os.path.join(dst_dir, '%s-%d%s' % (head, count, tail))
            
    return out_file
    
def open_file(out_file, fps):
    '''
    Please Note: writing to video with OpenCV can be a huge pain in the ass. Need to find a better way.
    most file formats/Codecs simply don't work (they fail silently without writing a file).
    You need to get the file extension/codec combination correct, and this is bloody difficult!
    
    The only codec that works reliably is MJPEG with .avi extension, but this results in huge files.
    '''      
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    
    if not out_file.endswith(".avi"):
        head, tail = os.path.splitext(os.path.basename(out_file))
        log.warn("This is unlikely to work! If you really want %s output, you should use ffmpeg (the -F option) which will make a proper %s file" % (tail, head+tail))
    
    if out_file.endswith(".mp4"):
        fourcc = cv2.VideoWriter_fourcc(*'X264')  #mp4 (doesn't work without the right codecs installed)
        log.info("Writing MP4 file %s" % out_file)
    elif out_file.endswith(".avi"):
        #fourcc = cv2.VideoWriter_fourcc(*'XVID') #avi
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        log.info("Writing AVI file %s" % out_file)
    elif out_file.endswith(".mkv"):
        fourcc = cv2.VideoWriter_fourcc(*'H264') #avi
        log.info("Writing H264 file %s" % out_file)
    else:
        log.info("Writing MJPG file %s" % out_file)
      
    out = cv2.VideoWriter(out_file, fourcc, fps, (480, 640))
    return out
    
def open_ffmpeg_file(out_file, fps, quality=25, show_output='quiet', FFMPEG_BINARY='ffmpeg'):
    '''
    use ffmpeg to write output video file. can use more codecs (smaller files), but messier
    '''     
    out = VideoWriter(FPS=fps,outFile=out_file,quality=quality,show_output=show_output,FFMPEG_BINARY=FFMPEG_BINARY)
    return out
    
def post_process_ffmpeg_thread(out_file, new_file, remove_org=False, quality=30, show_output='quiet', FFMPEG_BINARY='ffmpeg'):
    t = threading.Thread(target=post_process_ffmpeg, name="ffmpeg", args=(out_file, new_file, remove_org, show_output, FFMPEG_BINARY)) #post process file in background
    log.info('Starting ffmpeg post processing thread {}'.format(t))
    t.daemon = True
    t.start()
    
def post_process_ffmpeg(out_file, new_file, remove_org=False, quality=30, show_output='quiet', FFMPEG_BINARY='ffmpeg'):
    '''
    post process output video file with ffmpeg.
    only useful for MJPEG files that are huge, to compress them
    ''' 
    command = '%s -y -i %s -an -movflags faststart -crf %d -v %s %s' % (FFMPEG_BINARY, out_file, quality, show_output, new_file) #enable faststart if you want to stream from a web page
    #command = '%s -y -i %s -an -crf %d -v %s %s' % (out_file, quality, show_output, new_file)
    log.info("Post processing %s to %s for better compression" % (out_file, new_file))

    try:
        subprocess.check_output(command.split(" "))
        log.info("file %s Written" % new_file)
        if remove_org:
            os.unlink(out_file)
            log.info("file %s deleted" % out_file)
    except subprocess.CalledProcessError as e:
        log.error("Error processing file %s, %d, %s" % (out_file, e.returncode, e.output))
    
def main():
    global log
    
    parser = argparse.ArgumentParser(description='Record time lapse video of 3DWOX printer in action')
    parser.add_argument('-o','--out', action='store',help='Destination File Name defaults to the model name.avi', default=None)
    parser.add_argument('-od','--outdirectory', action='store',help='Destination directory (default=current directory)', default='./')
    parser.add_argument('-f','--fps', action='store',type=int, default=10, help='min playback speed, 1=real time, 10=10X real time etc default=10')
    parser.add_argument('-t','--time', action='store',type=int, default=300, help='optional max recording time in seconds. 0=unlimited. Set max duration of video, and fps is calculated automatically (but not less than min frame rate). Default=300')
    parser.add_argument('-u','--url', action="store", default='192.168.100.204', help='url/IP to read image from (default=192.168.100.204)')
    parser.add_argument('-p','--port', action="store", type=int, default=80, help='url port (default=80)')
    parser.add_argument('-pr','--postroll', action="store", type=int, default=5, help='seconds of video to capture after print complete (default=5)')
    parser.add_argument('-l','--log', action="store",default="~/3DPrinter_video.log", help='main log file. Set to None to disable logging. (default=~/3DPrinter_video.log)')
    parser.add_argument('-d','--daemon', action='store_true', help='run as daemon (ie never exit, just loop)', default = False)
    parser.add_argument('-Fx','--ffmpegexecutable', action="store",default="ffmpeg", help='path and name of ffmpeg executable(default=ffmpeg)')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('-P','--postprocess', action='store_true', help='post process video file with ffmpeg to reduce size', default = False)
    action.add_argument('-F','--ffmpeg', action='store_true', help='use ffmpeg for writing file (not OpenCV)', default = False)
    parser.add_argument('-R','--deleteoriginal', action='store_false', help='delete original file after post processing video file with ffmpeg', default = True)
    parser.add_argument('-Q','--quality', action='store',type=int, default=30, help='ffmpeg record Quality, lower is better (but bigger file), max 31 default=30')
    parser.add_argument('-X','--force', action='store_true', help='force record (for debugging) without checking status', default = False)
    parser.add_argument('-D','--debug', action='store_true', help='debug mode', default = False)
    parser.add_argument('-V', '--version', action='version', version="%(prog)s ("+__version__+")")

    arg = parser.parse_args()

    #----------- Logging ----------------
    
    if arg.debug:
        log_level = logging.DEBUG
        show_output = 'info'    #for ffmpeg output
    else:
        log_level = logging.INFO
        show_output = 'quiet'
        
    log_file=[os.path.normpath(os.path.expanduser(arg.log))]
    
    setup_logger('Main', log_file, level=log_level, console=True)
    setup_logger('Secondary', log_file, level=log_level, console=False)
    
    log = logging.getLogger('Main')                       #set up Main logging
    log_to_file = logging.getLogger('Secondary')          #set up non console logging
    
    log.info("****** Program Started ********")
    log.debug("Debug Mode")
    log.info("Logging to file: %s" % log_file[0])
    
    if arg.out is None:
        out_dir = os.path.normpath(arg.outdirectory)
    else:
        out_dir, arg.out = os.path.split(arg.out)
        out_dir = os.path.normpath(out_dir)

    if not os.path.isdir(out_dir):
        log.error("Directory '%s' does not exist, please create it first, before using it" % out_dir)
        sys.exit(1)
    log.info("Writing output files to: %s" % out_dir)
    
    
    if arg.time <= 0:
        arg.time = None
        
    FFMPEG_BINARY = arg.ffmpegexecutable
    tmp_file_short = None
    
    modes = {"idle":[10004,10006,10007], "printing":[10002,10003,10018,10023,10021], "invalid":[9999], "busy":[10001,10006,10028], "debug":[0]} #10028 bed moving?completing?, 100022?
        
    #urls
    url = "http://%s:%d/?action=snapshot" % (arg.url, arg.port)
    data_url = "http://%s:%d/cgi-bin/config_periodic_data.cgi" % (arg.url, arg.port)
    
    log.debug("URL: %s" % url)
    
    force = arg.force   #force recording, even if not printing (for debugging)
    if force:
        log.info("Recording without checking status...")
    else:
        PrintJobStatus = get_printer_status(data_url)
        log.info("waiting for printer response...")
        while PrintJobStatus in modes["invalid"]:
            time.sleep(1)
            PrintJobStatus = get_printer_status(data_url)
        
        log.info("Printer online, status: %d (%s)" % (PrintJobStatus, get_mode(PrintJobStatus,modes) ))
        
        if PrintJobStatus in modes["idle"]:
            log.info("Waiting to start Recording, please send/load file to printer")
            while PrintJobStatus in modes["idle"]:
                PrintJobStatus = get_printer_status(data_url)
                time.sleep(1)
     
    #max input frame rate is 3 fps (0.33 s per frame), but we acquire at 1 fps
    acq_spf = 1
    frames = 0
    writing = False

    #get_img = url_to_image_generator(url)  #not working...
    
    while True: #main loop
        try:
            start = time.time()
 
            print_data = get_data(data_url)
            PrintJobStatus = print_data['PrintJobStatus'] if not force else 0
            
            if not writing and (PrintJobStatus in modes["printing"] or PrintJobStatus in modes["debug"]):
                writing = True  #start recording
                started = time.time()
                opacity = 1.0
                duration = print_data['Estimatetime']/arg.fps   #of the video
                #file name
                if arg.out is None:
                    if arg.ffmpeg or arg.postprocess:
                        out_file = get_filename(print_data['model_name'], ".mp4", out_dir)   #default is .mp4 for ffmpeg file
                    else:
                        out_file = get_filename(print_data['model_name'], ".avi", out_dir)   #default is .avi file
                else:
                    out_file = get_filename(arg.out, out_dir=out_dir)
                out_file_short = os.path.basename(out_file)
                #duration    
                if arg.time is None:
                    fps = max(1, arg.fps)
                    duration_st = '(preset framerate, unlimited duration)'
                else:
                    max_duration = arg.time
                    fps = max(arg.fps, print_data['Estimatetime']/max_duration)
                    if print_data['Estimatetime']/fps < max_duration:
                        duration = print_data['Estimatetime']/fps
                    else:
                        duration = max_duration
                    duration_st = '(min framerate %dX, max duration: %s, actual duration: %s)' % (arg.fps, datetime.timedelta(seconds=max_duration), datetime.timedelta(seconds=duration))
                #output file processing
                if arg.ffmpeg:
                    ffmpeg_st = 'ffmpeg output, Quality: %d' % arg.quality
                    out = open_ffmpeg_file(out_file, fps, arg.quality, show_output, FFMPEG_BINARY)
                elif arg.postprocess:
                    tmp_file = get_filename("tmp_"+out_file_short, ".avi", out_dir)     #out_file is now temporary file
                    tmp_file_short = os.path.basename(tmp_file)
                    ffmpeg_st = 'OpenCV Output, ffmpeg post processing (to file: %s), Quality: %d' % (out_file_short,arg.quality)
                    out = open_file(tmp_file, fps)
                else:
                    ffmpeg_st = 'OpenCV Output'
                    out = open_file(out_file, fps)
                    
                dest_file = out_file_short if tmp_file_short is None else tmp_file_short    
                postroll = arg.postroll*fps
                log.info("Printing: %s, Material:%s, colour:%s, from:%s Output: %s.\r\nRecording at %dX realtime %s. Estimated print time: %d:%d, completed at: %s" % ( print_data['model_name'],
                                                                                                                                                                        print_data['material_name'],
                                                                                                                                                                        print_data['material_color_name'],
                                                                                                                                                                        "cloud" if print_data['cloud_print'] else "Local", 
                                                                                                                                                                        ffmpeg_st, 
                                                                                                                                                                        fps, 
                                                                                                                                                                        duration_st, 
                                                                                                                                                                        print_data['hours'], 
                                                                                                                                                                        print_data['mins'], 
                                                                                                                                                                        datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(seconds=print_data['Estimatetime'])))
                
            if writing:
                #img = next(get_img)    #generator not working for url so just read the url
                img = url_to_image(url)
                img = rotate_img(img, 90)
                
                elapsed_time = datetime.timedelta(seconds=int(time.time()-started))
                
                if frames % fps == 0:   #fade text
                    opacity = max(0.6, opacity - 0.01)
                img_txt = overlay_text(img, out_file_short, started, PrintJobStatus, fps, print_data, duration, modes, opacity, extra_text=(time.time()-started < 30*fps))
                
                out.write(img_txt)  #write frame to the output video
                
                frames += 1
                
                if frames % 30 == 0 and not os.path.exists(out_file):
                    log.warn("Output file %s is not being written:" % out_file)
                    
                if print_data['filamentRemain'] == print_data['filamentSub']:   #single filament
                    suffix_str = "time remaining %d:%d, remaining fil: %d%% %s         " % (print_data['hours'],
                                                                                            print_data['mins'],
                                                                                            print_data['filamentRemain'], 
                                                                                            elapsed_time)
                else:
                    suffix_str = "printing %s, %s, time remaining %d:%d, remaining fil1: %d%% fil2: %d%% %s         " % (   print_data['material_name'],
                                                                                                                            print_data['material_color_name'],
                                                                                                                            print_data['hours'],
                                                                                                                            print_data['mins'],
                                                                                                                            print_data['filamentRemain'], 
                                                                                                                            print_data['filamentSub'], 
                                                                                                                            elapsed_time)
                if log_level == logging.DEBUG:
                    log.debug("Wrote %d frames (%d bytes) at %dfps, %scomp: %d%%, PrintJobStatus: %d(%s) bed_temp:%d noz_temp:%d %s" % (frames,
                                                                                                                                        len(img), 
                                                                                                                                        fps, 
                                                                                                                                        'to: '+dest_file+' ' if frames % 1000 == 0 else '', 
                                                                                                                                        print_data['percent'],
                                                                                                                                        PrintJobStatus, 
                                                                                                                                        get_mode(PrintJobStatus, modes), 
                                                                                                                                        print_data['bed_temp'], 
                                                                                                                                        print_data['nozzel_temp'], 
                                                                                                                                        suffix_str.replace("remaining","rem")))
                else:
                    log_to_file.info("Wrote %d frames (%d bytes) at %dfps to file: %s, completed: %d%%, %s" % (frames, len(img), fps, dest_file, print_data['percent'], suffix_str))
                    print_progress(print_data['percent'], 100, prefix=dest_file, suffix=suffix_str, decimals=0, bar_length=40)
            
            if writing and (PrintJobStatus in modes["idle"] or PrintJobStatus in modes["invalid"]):
                log.info("\nPrinting finished at %s" % (time.ctime()))
                log.debug("writing postroll frames: %d (%ds)" % (postroll, arg.postroll))
                opacity = 1.0
                img_txt = overlay_text(img, out_file_short, started, PrintJobStatus, fps, print_data, duration, modes, opacity)
                while postroll > 0:
                    out.write(img_txt)  #write last frame to the output video
                    postroll -= 1
                frames = 0
                writing = False
                tmp_file_short = None
                if arg.daemon:
                    out.release()
                    log.info("file: %s written" % out_file)
                    if arg.postprocess:
                        post_process_ffmpeg_thread(tmp_file, out_file, arg.deleteoriginal, arg.quality, show_output, FFMPEG_BINARY)
                    time.sleep(20)
                    log.info("Waiting to start Recording, please send/load file to printer")
                else:
                    break
            
            while time.time()-start < acq_spf:  #delay before we read the next frame
                time.sleep(0.1)
            
        except (KeyboardInterrupt, SystemExit):
            log.info("\nSystem exit Received - Exiting program")
            break

    try:
        out.release()
    except ValueError:
        pass
    log.info("file: %s written" % out_file)
    if arg.postprocess:
        post_process_ffmpeg(tmp_file, out_file, arg.deleteoriginal, arg.quality, show_output, FFMPEG_BINARY)
        
if __name__ == "__main__":
    main()
