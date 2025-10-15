import cv2
import os


def main():
    # Initialize the camera
    cap = cv2.VideoCapture(0)  # 0 for default camera, you can change it to other indices if you have multiple cameras

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    # Create directory to save images if it doesn't exist
    save_dir = 'captured_images'
    os.makedirs(save_dir, exist_ok=True)

    # Loop to discard initial frames until a clear frame is captured
    clear_frame = None
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if frame is captured successfully
        if not ret:
            print("Error: Failed to capture frame")
            break

        # Display the captured frame
        cv2.imshow('Camera', frame)

        # Check if frame is clear and stable
        if clear_frame is None:
            clear_frame = frame.copy()
        else:
            diff = cv2.absdiff(frame, clear_frame)
            mean_diff = diff.mean()
            if mean_diff < 2:  # Adjust threshold as needed
                break

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Loop to continuously capture frames from the camera
    count = 0
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if frame is captured successfully
        if not ret:
            print("Error: Failed to capture frame")
            break

        # Display the captured frame
        cv2.imshow('Camera', frame)

        # Check if frame is blank
        if frame.mean() < 2:  # Adjust threshold as needed
            continue  # Skip saving blank frames

        # Save the captured frame
        img_name = f"image_{count}.jpg"
        img_path = os.path.join(save_dir, img_name)
        cv2.imwrite(img_path, frame)

        # Increment count for the next image
        count += 1

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()