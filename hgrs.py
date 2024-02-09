# import necessary packages
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model
import autopy

# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Load the gesture recognizer model
model = load_model('mp_hand_gesture')

# Load class names
f = open('gesture.names', 'r')
classNames = f.read().split('\n')
f.close()
print(classNames)

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read each frame from the webcam
    _, frame = cap.read()

    x, y, c = frame.shape

    # Flip the frame vertically
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get hand landmark prediction
    result = hands.process(framergb)

    # print(result)
    
    className = ''

    # post process the result
    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                # print(id, lm)
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)

                landmarks.append([lmx, lmy])

            # Drawing landmarks on frames
            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

            # Predict gesture
            prediction = model.predict([landmarks])
            # print(prediction)
            classID = np.argmax(prediction)
            className = classNames[classID]
            
            # Get the position of the index finger tip
            if classID == 1:  # Assuming index finger gesture corresponds to class 1
                index_finger_tip_x, index_finger_tip_y = landmarks[8]

                # Map the index finger position to screen resolution
                screen_width, screen_height = autopy.screen.size()
                mapped_x = int(np.interp(index_finger_tip_x, [0, x], [0, screen_width]))
                mapped_y = int(np.interp(index_finger_tip_y, [0, y], [0, screen_height]))

                # Move the mouse cursor
                autopy.mouse.move(mapped_x, mapped_y)
                
            elif classID == 5:  # Assuming three fingers shown corresponds to class 5
                # Perform left click
                autopy.mouse.click()
                
            elif classID == 2:  # Assuming open hand gesture corresponds to class 2
                # Perform right click
                autopy.mouse.click(button=autopy.mouse.Button.RIGHT)

    # show the prediction on the frame
    cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (0,0,255), 2, cv2.LINE_AA)

    # Show the final output
    cv2.imshow("Output", frame) 

    if cv2.waitKey(1) == ord('q'):
        break

# release the webcam and destroy all active windows
cap.release()
cv2.destroyAllWindows()
