import cv2
import os

# Step 1: Make sure the images directory exists
if not os.path.exists("images"):
    os.makedirs("images")

# Step 2: Ask for the student's name in the terminal
student_name = input("Enter the student's name for enrollment: ")

# Make sure they didn't leave it blank
if len(student_name.strip()) == 0:
    print("Name cannot be empty. Enrollment cancelled.")
    exit()

print(f"Starting webcam to enroll '{student_name}'.")
print("--> Press 'c' to Capture the photo.")
print("--> Press 'q' to Quit without saving.")

# Step 3: Initialize the webcam
video_capture = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = video_capture.read()
    
    if not ret:
        print("Failed to grab frame.")
        break

    # Show instructions on the webcam window
    cv2.putText(frame, "Press 'c' to Capture, 'q' to Quit", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Display the video feed
    cv2.imshow("Student Enrollment", frame)

    # Wait for key press
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        # Step 4: User pressed 'c', save the image!
        # Create a file path like "images/Shrav.jpg"
        image_path = f"images/{student_name}.jpg"
        
        # Save the current frame to that file path
        cv2.imwrite(image_path, frame)
        
        print(f"Success! Image saved as {image_path}")
        break  # Exit the loop after saving

    elif key == ord('q'):
        # User pressed 'q', cancel enrollment
        print("Enrollment cancelled.")
        break

# Clean up
video_capture.release()
cv2.destroyAllWindows()
