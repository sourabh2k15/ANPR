'''
The main module that keeps waiting for a button press event forever and whenever there is one, captures image from cam, detects plate, recognizes it and displays plate on lcd

subprocess is a module that allows a python script to execute commands in terminal and return output
RPi.GPIO is the module required to interact with raspberry pi's GPIO pins, which help in interfacing push button and 16*2 lcd

time module is required to give a delay ( time.sleep(seconds) after button is pressed ) 

'''

from subprocess import call
import RPi.GPIO as GPIO
import time
    
in_img  = "in.png"		#input image | image location to be saved for webcam captured image 
out_img = "out.png"		#output plate image location, where platedetect.py saves plate image

GPIO.setmode(GPIO.BCM)		#using BCM numbering for GPIO pins ( broadcom mode )

# Input button setup
# GPIO pins have inbuilt pull up and pull down resistors , here we have connected our push button between 18 and GND . 18 is set to 3.3 V as its pull up resistor has been enabled by the 3rd argument in GPIO.setup()
# Now when the button is pressed the input from GPIO 18 will stop or become low / False . 
 
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)	

#the script runs forever , waiting for a false input from GPIO 18 , meaning button was pressed and the action begins!

while True:
    input_state = GPIO.input(18) #reading GPIO 18 input, if false start process 
        	
    if input_state == False: 
    	#step 1: capture image from webcam using fswebcam , various arguments can be passed like resolution, fps, save location, etc
	call(["fswebcam","--device","/dev/video1","--resolution","800x600","--skip","1","--fps","15","--save",in_img])
	
	#step 2: detect plate and seperate it out using localization algorithm in platedetect.py
	call(["python","platedetect.py",in_img,out_img])	
	
	#step 3: pass plate image to tesseract, which does OCR and gives text of number plate
	call(["tesseract",out,"out"])
	
	#reading text and displaying on lcd 
	n = open("out.txt","r")
	platetext = n.read()
	call(["sudo","python","lcdgpio.py",platetext])
        
        time.sleep(1)
