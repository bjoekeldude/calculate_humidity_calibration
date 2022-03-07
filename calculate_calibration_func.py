#!python3

import sys
import getopt
from tracemalloc import Statistic
import numpy as np
import matplotlib.pyplot as plt
from xml.etree.ElementTree import tostring
import statistics
import math

def help_text():
    print("Humidity-Calibrator (2022 March 07)")
    print(" ")
    print("Usage: calculate_calib_func [arguments]  calculates calibration from two measurement rows")
    print(" ")
    print("Arguments:")
    print("       -n <filename>                     Input of Zero-Measure")
    print("       -m <filename>                     Input of Max-Measure")
    print("       -f <filename>                     Save Values to File")

def version_text():
    print("Version 1.0 written by Stephan Bökelmann, stephan.boekelmann@thga.de")

filename = "calibration_data"
zero_file = "zf"
max_file = "mf"

argv = sys.argv[1:]

try:
    opts, args = getopt.getopt(argv, "n:m:f:hv",
        ["nullmessung =", "maxmessung =","filename ="])
except:
    print("Incorrect usage")
    help_text()

for opt, arg in opts:
    if opt in ['-n', '--nullmessung']:
        zero_file = arg
    elif opt in ['-m', '--maxmessung']:
        max_file = arg
    elif opt in ['-f', '--filename']:
        filename = arg
    elif opt in ['-h']:
        help_text()
        exit()
    elif opt in ['-v']:
        version_text()
        exit()


if zero_file == "zf":
    print("Incorrect Calling-Parameters please specify Zero-Measurement")
    help_text()
elif max_file == "mf":
    print("Incorrect Calling-Parameters please specify Max-Measurement")
    help_text()

zero_file_handle = open(zero_file, "r")
max_file_handle = open(max_file, "r")

zero_content = zero_file_handle.read()
max_content = max_file_handle.read()

zero_measure_list = zero_content.split("\n")
max_measure_list = max_content.split("\n")



print(" ")    
print("Calculating Calib-Values from "+zero_file+" for Zero-Measurement and "+max_file+" for Max-Measurement")
print("Printing values into "+filename)
print(" ")

number_zero_values = len(zero_measure_list)-1
number_max_values = len(max_measure_list)-1

print("Zero-Measurement runs with "+str(number_zero_values))
print("Max-Measurement runs with "+str(number_max_values))

zero_measure_list_int = list(map(int, zero_measure_list[:-1]))
max_measure_list_int  = list(map(int, max_measure_list[:-1]))

zero_mean = statistics.mean(zero_measure_list_int)
zero_stdev = statistics.stdev(zero_measure_list_int)

max_mean = statistics.mean(max_measure_list_int)
max_stdev = statistics.stdev(max_measure_list_int)

print("Zero-Mean = "+str(round(zero_mean,2)))
print("Max-Mean = "+str(round(max_mean,2)))

count, bins, ignored = plt.hist(zero_measure_list_int, 30, density=True)
plt.plot(bins, 1/(zero_stdev * np.sqrt(2 * np.pi)) *
               np.exp( - (bins - zero_mean)**2 / (2 * zero_stdev**2) ),
         linewidth=2, color='r')

count_max, bins_max, ignored_max = plt.hist(max_measure_list_int, 30, density=True)
plt.plot(bins_max, 1/(max_stdev * np.sqrt(2* np.pi)) *
                np.exp( - (bins_max - max_mean)**2 / (2 * max_stdev**2) ),
         linewidth=2, color='g')

plt.show()

standartfehler = max((zero_stdev/math.sqrt(number_zero_values)),
                        (max_stdev/math.sqrt(number_max_values)))

print("Die Standartfehler für den gegebenen Sensor berträgt "+str(standartfehler))

print("Die Standartabweichung beträgt für die Nullmessung "+str(round(zero_stdev,2))+" Counts")
print("Die Standartabweichung beträgt für die Maxmessung "+str(round(max_stdev,2))+" Counts")

abszisse = [zero_mean, max_mean]
ordinate = [0, 100]
plt.plot(abszisse, ordinate)
plt.errorbar(abszisse, ordinate, xerr = standartfehler, fmt = 'x' )
plt.show()

steigung = 100/(max_mean - zero_mean)

print("Die Steigung der Kalibrationsgeraden beträgt "+str(round(steigung, 3))+"%rF pro Count")
print("Kalibrationsgleichung ergibt sich zu: %rF(Cnt) = "+str(round(steigung, 3))+"%rF * (Cnt - " 
        +str(round(zero_mean,3)) +" Cnt)")
print("Die Messunsicherheit beträgt Standartabweichung * Steigung = "
        +str(round((max(zero_stdev,max_stdev)*steigung),1))+" %rF")

filehandle = open(filename, "w")
filehandle.write("%rF(Cnt) = "+str(round(steigung, 3))+" * (Cnt - "+str(round(zero_mean,3))+" Cnt)")
filehandle.close()