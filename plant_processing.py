import cv2
import numpy as np

## Function for color thresholding for plants
def colorThreshold(img):
    # Convert color image to hsv range
    temp_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Green mask hsv image
    lower_green = np.array([36, 25, 25]) # Range should be dynamic
    higher_green = np.array([70, 255,255])
    temp_img = cv2.inRange(temp_img, lower_green, higher_green)
    # Green mask produces black and white image with green pixels as white

    # Apply opening and closing for noise reduction --beta
    kernel = np.ones((5,5),np.uint8)
    temp_img = cv2.morphologyEx(temp_img, cv2.MORPH_OPEN, kernel)
    temp_img = cv2.morphologyEx(temp_img, cv2.MORPH_CLOSE, kernel)

    return temp_img


def computeCircleGreen(img):
    ## Identifies the circle arround the plant and no. of green pixels
    # returns circle applied image
    # prints total green pixel count, area, ratio of the two

    ## Erosion
    #greenMask1 = cv2.erode(greenMask1,kernel,iterations = 1)
    ## Dialation
    #kernel_dialation = np.ones((2,2),np.uint8)
    #greenMask1 = cv2.dilate(greenMask1,kernel_dialation,iterations = 1)

    # Applying guassian blur
    #img = cv2.GaussianBlur(img, (5,5), 0)

    # color thresholding plants
    temp_img = colorThreshold(img)

    # Counting and storing white pixels 
    white_pixels = []
    # total white pixels equals toal green pixels
    white_pixels_count = 0
    for y, row in enumerate(temp_img):
        for x, px in enumerate(row):
            if px == 255:
                white_pixels_count += 1
                white_pixels.append((x, y))
    # Enclosing white pixels in a circle
    center, radius = cv2.minEnclosingCircle(np.array([white_pixels], dtype=np.int32))

    # Applying circle in image and calculating ratio
    PI = 3.14
    temp_img = img
    cv2.circle(img,(int(round(center[0])),int(round(center[1]))), int(round(radius)), (0,0,255), 2)
    print("Green pixels of image  = ", white_pixels_count)
    area = PI * radius * radius
    print("Area of the cirlce = ", area)
    print("Concentration of the green pixels = ", white_pixels_count/area)

    # Return circle applied image
    return temp_img


# Load images
img1 = cv2.imread('plant.jpg')
img2 = cv2.imread('plant2.jpg')
img3 = cv2.imread('plant3.jpg')
img4 = cv2.imread('plant4.jpg')



img1 = computeCircleGreen(img1)
img2 = computeCircleGreen(img2)
img3 = computeCircleGreen(img3)
img4 = computeCircleGreen(img4)

# Show image
cv2.imshow('plant1', img1)
cv2.imshow('plant2', img2)
cv2.imshow('plant3', img3)
cv2.imshow('plant4', img4)
print ("Image Output Complete")

#cv2.imshow('plant mask1', greenMask1)
#cv2.imshow('plant mask2', greenMask2)
#cv2.imshow('plant mask3', greenMask3)
#cv2.imshow('plant mask4', greenMask4)

cv2.waitKey(0)
cv2.destroyAllWindows()