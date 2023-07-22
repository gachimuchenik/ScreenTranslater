import cv2
import numpy as np

def crop_image(image, coordinates):
    """ Crop area from image
    :param image: input image
    :param coordinates: [x1, y1, x2, y2]
    :return: cropped image
    """ 
    x1 = coordinates[0]
    x2 = coordinates[2]
    y1 = coordinates[1]
    y2 = coordinates[3]
    return image[y1:y2, x1:x2]

def grayscale_image(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def denoiser(image):
    return cv2.medianBlur(image, 3)

def gaussian_blur(image):
    return cv2.GaussianBlur(image, (3,3), 0)

def bilateral_filter(image):
    return cv2.bilateralFilter(image, 3, 75, 75)

def thresholding(image):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, -40)

def canny(image):
    return cv2.Canny(image=image, threshold1=100, threshold2=200) 

def kmeans(image):
    Z = image.reshape((-1,3))
    Z = np.float32(Z)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 4
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((image.shape))

    return res2

def resize(image):
    scale_percent = 50 # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    # resize image
    return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)