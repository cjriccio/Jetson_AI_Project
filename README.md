# Jetson_AI_Project
My screen saver project for the Jetson AI course

This program uses a Resnet18 image classification model to determine whether or not I am sitting in front of the computer and turn off and on the monitor display accordingly. If it detects that I am absent for more than 5 seconds, the display will be turned off. If the display is off and it detects that I am present in front of the monitor, it will turn the display back on. This is more efficient than most screensavers, which simply turn off the display after a period of time without user input. This program would save more power and could extend the battery life of devices like laptops and phones.

Demonstration video: https://photos.app.goo.gl/qPj81kUnZfukpX2Z6


Set up instructions:

1: Instal the Jetson Inferences docker container: https://github.com/dusty-nv/jetson-inference

2: Download this project and place it in a file that the docker container will be able to locate

3: Start the docker container
$ cd jetson-inference
$ docker/run.sh --volume /(project file):/(project file)


Running the program:

$ cd (ssav file path)

$ python3 screensave.py --model=resnet18.onnx --labels=labels.txt --input_blob=input_0 --output_blob=output_0 /dev/video0


This model was trained to detect my face, and would likely not turn the screen on for another person. While this could be beneficial by adding a layer of security and preventing other people from viewing my information if I get up from my computer for a moment, it also means other users must train their own model for the program to run as intended for them.

Model training instructions: 

1: Use the camera-capture feature of the Jetson-inference docker container as described here: https://github.com/dusty-nv/jetson-inference/blob/master/docs/pytorch-collect.md
$ camera-capture /dev/video0

2: Using the provided labels.txt file, collect “absent” and “present” data sets. The absent data set should contain at least 100 pictures of the background area located behind where you usually work without you in the pictures. The present data set should contain at least 100 pictures of yourself seated in front of your screen with your head at various positions and angles.

3: Train the model according to the instructions in the link above.
$ python3 train.py --model-dir=models/(YOUR-MODEL) data/(YOUR-DATASET)

4: Export model
$ python3 onnx_export.py --model-dir=models/(YOUR-MODEL)

5: Copy the exported model to the directory where the screensave script is and replace the resnet18.onnx file with it.
