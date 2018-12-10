from my_CNN_model import *
import cv2
import numpy as np
from keras.models import load_model
from keras.utils.generic_utils import custom_object_scope
from besoins import smoothL1, relu6, DepthwiseConv2D, mask_weights
import tensorflow as tf

def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

'''
with custom_object_scope({'smoothL1': smoothL1, 'relu6': relu6, 'DepthwiseConv2D': DepthwiseConv2D, 'mask_weights': mask_weights, 'tf': tf}):
            my_model= load_model("face_landmark_dnn_ousmane.h5")
             '''   
                
# Load the model built in the previous step
my_model = load_my_CNN_model('model_landmarks')


#model_landmarks_106

# Face cascade to detect faces
face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')

def draw_face_keypoints(img, label):
    img = img.astype(np.uint8)
    

    if label is not None:
        for i in range(0, 136, 2):
            x = int(label[i])
            y = int(label[i+1])
            cv2.circle(img, (x, y), 0, (255, 0, 0), 3)

    cv2.imshow("draw",img)

VIDEO_PATH = "钟镇涛_1030.avi"
# Load the video
camera = cv2.VideoCapture(VIDEO_PATH )

while True:
    # Grab the current paintWindow
    (grabbed, frame) = camera.read()
    frame = cv2.flip(frame, 1)

    #frame = cv2.resize(frame, (450, 450)) 

   
    frame2 = np.copy(frame)
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    #frame,faces = detectFaceDlibHog(hogFaceDetector,gray)
    

    for (x, y, w, h) in faces:

        # Grab the face
        gray_face = gray[y:y+h, x:x+w]
        color_face = frame[y:y+h, x:x+w]

        # Normalize to match the input format of the model - Range of pixel to [0, 1]
        gray_normalized = gray_face / 255

        # Resize it to 96x96 to match the input format of the model
        original_shape = gray_face.shape # A Copy for future reference
        face_resized = cv2.resize(gray_normalized, (96, 96), interpolation = cv2.INTER_AREA)
        face_resized_copy = face_resized.copy()
        face_resized = face_resized.reshape(1, 96,96,1)

        # Predicting the keypoints using the model
        keypoints = my_model.predict(face_resized)

       

       

        # De-Normalize the keypoints values
        keypoints = keypoints * 48 + 48
        
        
        

       

        

        # Map the Keypoints back to the original image
        face_resized_color = cv2.resize(color_face, (96, 96), interpolation = cv2.INTER_AREA)
        face_resized_color2 = np.copy(face_resized_color)

        # Pair them together
        points = []
        for i, co in enumerate(keypoints[0][0::2]):
            points.append((co, keypoints[0][1::2][i]))
      

        

        # Add KEYPOINTS to the frame2
        for (a,b) in points:
          
            #cv2.circle(face_resized_color2, keypoint, 1, (0,255,0))
            cv2.circle(face_resized_color2, (a, b), 1, (0, 255, 0), -1)
            

        frame2[y:y+h, x:x+w] = cv2.resize(face_resized_color2, (original_shape), interpolation = cv2.INTER_CUBIC)

        # Show the frame and the frame2
       
        cv2.imshow("Facial Keypoints", frame2)

        draw_face_keypoints(frame2,keypoints[0])
        

        # If the 'q' key is pressed, stop the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()