#!/usr/bin/python3

#cd jetson-inference
#docker/run.sh --volume ~/ssav:/ssav --device /dev/video0
#cd ../
#cd ssav
#python3 screensave.py --model=resnet18.onnx --labels=labels.txt --input_blob=input_0 --output_blob=output_0 /dev/video0

import subprocess
import time

import jetson.inference
import jetson.utils

import argparse
import sys


# parse the command line
parser = argparse.ArgumentParser(description="Classify a live camera stream using an image recognition DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.imageNet.Usage() +
                                 jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="googlenet", help="pre-trained model to load (see below for options)")
parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)


# load the recognition network
net = jetson.inference.imageNet(opt.network, sys.argv)
print(sys.argv)
# create video sources & outputs
input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv)
font = jetson.utils.cudaFont()

# process frames until the user exits
counter =0
screen_on=True
while True:
	# capture the next image
	img = input.Capture()

	# classify the image
	class_id, confidence = net.Classify(img)

	# find the object description
	class_desc = net.GetClassDesc(class_id)

	# overlay the result on the image	
	font.OverlayText(img, img.width, img.height, "{:05.2f}% {:s}".format(confidence * 100, class_desc), 5, 5, font.White, font.Gray40)
	
	# render the image
	output.Render(img)

	# update the title bar
	output.SetStatus("{:s} | Network {:.0f} FPS".format(net.GetNetworkName(), net.GetNetworkFPS()))

	# print out performance info
	net.PrintProfilerTimes()

	#turn screen on or off if present or absent
	if class_id==0000:
		counter += 1
		if counter > 50:
			print("Turning screen off")
			subprocess.run(["xset", "-display", ":0.0", "dpms", "force", "off"])
			screen_on=False
	
	else:
		counter = 0
		print("Turning screen on")
		subprocess.run(["xset", "-display", ":0.0", "dpms", "force", "on"])
		screen_on=True

	# exit on input/output EOS
	if not input.IsStreaming() or not output.IsStreaming():
		break
