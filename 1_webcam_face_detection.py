import cv2

# Step 1: Initialize the webcam
# 0 means the default camera on your computer
video_capture = cv2.VideoCapture(0)

# Step 2: Load the pre-trained face detection model from OpenCV
# This model uses "Haar Cascades" to find faces in an image
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("Webcam started. Press 'q' on the keyboard to exit.")

# Step 3: Create an infinite loop to continuously get frames from the webcam
while True:
    # Read a single frame (image) from the webcam
    # 'ret' is a boolean that tells us if the frame was read correctly
    # 'frame' is the actual image
    ret, frame = video_capture.read()

    # If the frame wasn't read correctly, stop the loop
    if not ret:
        print("Failed to grab frame")
        break

    # Step 4: Convert the frame to grayscale (black and white)
    # Face detection works much faster and better on grayscale images
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Step 5: Detect faces in the grayscale frame
    # This returns a list of rectangles [x, y, width, height] where faces are found
    faces = face_cascade.detectMultiScale(
        gray_frame,
        scaleFactor=1.1,  # Compensates for faces appearing smaller the further they are
        minNeighbors=5,   # How many neighboring boxes need to be detected to be confident it's a face
        minSize=(30, 30)  # Minimum size of a face to detect
    )

    # Step 6: Draw a rectangle around each detected face
    for (x, y, w, h) in faces:
        # cv2.rectangle(image, top_left_corner, bottom_right_corner, color_in_BGR, line_thickness)
        # BGR for Green is (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Step 7: Display the resulting frame on the screen
    cv2.imshow('Webcam - Face Detection (Press q to quit)', frame)

    # Step 8: Wait for the 'q' key to be pressed to break the loop
    # cv2.waitKey(1) waits 1 millisecond for a key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Step 9: Clean up when we are done
# Release the webcam so other programs can use it
video_capture.release()
# Close the window we opened
cv2.destroyAllWindows()
