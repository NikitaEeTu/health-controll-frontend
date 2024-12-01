import cv2
import dlib
import numpy as np
from collections import deque
from playsound import playsound
from threading import Thread


class FatigueDetection:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("eyesdetection/shape_predictor_68_face_landmarks.dat")
    EAR_THRESHOLD = 0.25
    BLINK_THRESHOLD_FRAMES = 3
    CALIBRATION_FRAMES = 50

    blink_count = 0
    consecutive_closed_frames = 0
    calibration_data = []
    calibrated_ear_threshold = EAR_THRESHOLD
    smoothed_ear_values = deque(maxlen=10)
    is_running = False

    @staticmethod
    def eye_aspect_ratio(eye):
        """Calculate the Eye Aspect Ratio (EAR)."""
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C)

    @staticmethod
    def calibrate_ear(ear_list):
        """Calibrate EAR threshold based on initial data."""
        return sum(ear_list) / len(ear_list)

    @staticmethod
    def process_frame(gray_frame, update_callback):
        """Process a single frame for fatigue detection."""
        faces = FatigueDetection.detector(gray_frame)
        for face in faces:
            landmarks = FatigueDetection.predictor(gray_frame, face)


            left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
            right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])


            ear_left = FatigueDetection.eye_aspect_ratio(left_eye)
            ear_right = FatigueDetection.eye_aspect_ratio(right_eye)
            ear = (ear_left + ear_right) / 2.0


            FatigueDetection.smoothed_ear_values.append(ear)
            smoothed_ear = sum(FatigueDetection.smoothed_ear_values) / len(FatigueDetection.smoothed_ear_values)


            if len(FatigueDetection.calibration_data) < FatigueDetection.CALIBRATION_FRAMES:
                FatigueDetection.calibration_data.append(smoothed_ear)
                if len(FatigueDetection.calibration_data) >= FatigueDetection.CALIBRATION_FRAMES:
                    FatigueDetection.calibrated_ear_threshold = FatigueDetection.calibrate_ear(
                        FatigueDetection.calibration_data
                    ) * 0.85
                update_callback("Calibrating")
                return


            if smoothed_ear < FatigueDetection.calibrated_ear_threshold:
                FatigueDetection.consecutive_closed_frames += 1
                if FatigueDetection.consecutive_closed_frames >= 15:
                    playsound('sounds/warning.mp3')  # Alert the user
                    update_callback("Tired")
            else:
                if FatigueDetection.consecutive_closed_frames >= FatigueDetection.BLINK_THRESHOLD_FRAMES:
                    FatigueDetection.blink_count += 1
                FatigueDetection.consecutive_closed_frames = 0
                update_callback("Not Tired")

    @staticmethod
    def start_detection(update_callback):
        """Start fatigue detection in a separate thread."""
        FatigueDetection.is_running = True

        def detection_loop():
            cap = cv2.VideoCapture(2)
            while FatigueDetection.is_running:
                ret, frame = cap.read()
                if not ret:
                    continue
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                FatigueDetection.process_frame(gray_frame, update_callback)
            cap.release()

        Thread(target=detection_loop, daemon=True).start()

    @staticmethod
    def stop_detection():
        """Stop the fatigue detection process."""
        FatigueDetection.is_running = False
