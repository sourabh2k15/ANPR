'''
@params in, out

in : input image path to be processed
out : path for extracted plate image to be saved

usage : python platedetect.py in out 

sys module is used for parsing command line arguments 
cv2 is the opencv python binding 
numpy is a library for efficient operations on large arrays , opencv stores images as numpy arrays and does all its processing on it 

'''

import sys
import cv2
import numpy as np

#function used later to validate contours and weeding out non-number plate contours
def validate(cnt):  
    x,y,w,h = cv2.boundingRect(cnt)  # rectangle ecompassing contour
    
    #x,y,w,h = left position in image, top position in image, width , height
    #initialized output as false , if contour passes our checks it is set to true
    
    output=False
   
    if ((w!=0) & (h!=0)):		    # width and height of contour shouldn't be 0	
        if (((w/h>2) & (w>h))):		    # width should be greater than height and aspect ratio should be greater than 2
            if((h*w<25000) & (h*w>5000)):   # contour containing plate has an area not too large or small			
            	output=True		    #can be adjusted 
                
    return output

#reading input and output locations
image_path = sys.argv[1]
out = sys.argv[2]

#read rgb image 
rgb_img = cv2.imread(image_path)

#converting rgb image to grayscale to save memory and processing
gray_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)

#running a gaussian filter to remove noise and make image better for sobel filter
blur=cv2.GaussianBlur(gray_img,(5,5),0)

#applying sobel edge detection to detect edges as number plate characters have sudden changes in color == sharp edges
sobelx=cv2.Sobel(blur, cv2.CV_8U, 1, 0, ksize=3)

#thresholding the image to make it binary , using otsu thresholding method to preserve image
_,th2=cv2.threshold(sobelx, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

#applying a morphological operation using a rectangular plate like structural element which would result in connecting the characters on the plate into a single rectangular blob which can then be detected
se=cv2.getStructuringElement(cv2.MORPH_RECT,(23,2))
closing=cv2.morphologyEx(th2, cv2.MORPH_CLOSE, se)

#detecting contours in image and then weeding out them sequentially to detect number plate based on width, height, area , location
im2,contours,heirarchy = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

imwidth = rgb_img.shape[0]	# width of rgb input image
imheight = rgb_img.shape[1]	# height of rgb input image

#0 filled array initialed, this will later store plate image data as array
plate = np.array(0)

#if showContours is set to True, we can see a contours.png saved on disk, showing all contours 
# green border is for all contours detected 
# blue border is for contours passing validate() conditions , height, width, area
# white is for the number plate which is the only contour passing validate() and location in image is satisying certain conditions
showContours = False

#looping over all contours to check for validation and find one containing number plate
for i in range(len(contours)):
    cnt = contours[i] # stored current contour for processing
    x,y,w,h = cv2.boundingRect(cnt)
    
    if showContours == True:
 	cv2.rectangle(rgb_img,(x,y),(x+w,y+h),(0,255,0),2)
    
    if validate(cnt):
	if showContours == True:
		cv2.rectangle(rgb_img,(x,y),(x+w,y+h),(255,0,0),2)
	
	# if validate passed then check for location of contour in image	   
	# contour should not be towards the ends of the image, but rather towards the center in x direction and more downwards in y 		# direction 
	if (x>(imwidth/10) and x<((imwidth*9)/10)):
	    if(y>(imheight*2/10)):
	    	 # store plate image data in plate
		 plate = rgb_img[y:y+h,x:x+w]
	
		 if showContours == True:
			cv2.rectangle(rgb_img,(x,y),(x+w,y+h),(255,255,255),3)	

# write plate image data to disk at out location		    		
cv2.imwrite(out,possibleplate)

# if user wants to see contours in input rgb image, it is stored on disk at contours.png when showContours is set True
if showContours == True:
	cv2.imwrite("contours.png",rgb_img)

