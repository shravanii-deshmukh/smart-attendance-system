import cv2
import face_recognition
import os

# Step 1: Prepare our known faces
# We need to give the system a picture of someone it should recognize.
# Make sure you have an image inside the 'images' folder!
image_path = "images/person1.jpg" # <--- IMPORTANT: We will change this name!

# Check if the image exists before proceeding
if not os.path.exists(image_path):
    print(f"Error: Could not find the image '{image_path}'.")
    print("Please put a picture of yourself in the 'images' folder and update the code!")
    exit()

print("Loading known face... Please wait.")
# Load the image file
known_image = face_recognition.load_image_file(image_path)

# Extract the "face encodings" (unique facial features mapped as numbers)
# [0] grabs the first face found in the picture
known_face_encoding = face_recognition.face_encodings(known_image)[0]

# We will store our known encodings and their corresponding names in lists
known_face_encodings = [known_face_encoding]
known_face_names = ["My Name"] # <--- Change this to your actual name

print("Face loaded successfully! Starting webcam...")

# Step 2: Initialize webcam
video_capture = cv2.VideoCapture(0)

while True:
    # Read frame from webcam
    ret, frame = video_capture.read()
    if not ret:
        break

    # Step 3: Face Recognition needs RGB images (OpenCV uses BGR by default)
    # So we must convert the color format before passing it to face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Step 4: Find all faces and their encodings in the current webcam frame
    # We use a faster model called 'hog' (Histogram of Oriented Gradients)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Step 5: Loop through every face found in the webcam
    # We zip locations and encodings so we can process them together
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        
        # Default name if we don't recognize the person
        name = "Unknown"

        # Compare the face in the webcam against our known faces
        # tolerance=0.6 is default. Lower number is stricter.
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)

        # If a match was found in known_face_encodings, use the known name
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Step 6: Draw a box around the face and write the name
        # Draw the rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Step 7: Display the video feed
    cv2.imshow('Webcam - Face Recognition', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
video_capture.release()
cv2.destroyAllWindows()
