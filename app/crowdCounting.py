import cv2
import pandas as pd
import subprocess
import os

class_list = ["person"]

def get_person_coordinates(model, frame):
    results = model.predict(frame, verbose=False)
    a = results[0].boxes.data.detach().cpu()
    px = pd.DataFrame(a).astype("float")

    person_coords = []
    for _, row in px.iterrows():
        x1, y1, x2, y2 = row[0], row[1], row[2], row[3]
        class_id = int(row[5])
        if class_list[class_id] == 'person':
            person_coords.append([x1, y1, x2, y2])
    return person_coords

def annotate_and_count(model, input_path, output_path=None):
    """Process video/image, annotate, and calculate crowd count."""
    cap = cv2.VideoCapture(input_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    


    text = "People: 99"
    font_scale = frame_width / 1000
    font_scale = max(0.5, min(font_scale, 2))
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 3
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = 60
    y = 80
    if x + text_width > frame_width:
        x = frame_width - text_width - 60
    if y + text_height > frame_height:
        y = frame_height - text_height - 80
        
        


    if total_frames > 1:  # Video
        if output_path is None:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_counted.mp4"
            
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", f"{frame_width}x{frame_height}",
            "-r", str(int(fps)),
            "-i", "-",
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p",
            output_path,
        ]
        process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

        total_people = 0
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            person_coords = get_person_coordinates(model, frame)
            for bbox in person_coords:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

            people_count = len(person_coords)
            total_people += people_count
            frame_count += 1
            
            text = f"People: {people_count}"
            cv2.putText(
                frame,
                text,
                (x, y),
                font,
                font_scale,
                (0, 0, 0),
                thickness
            )
            process.stdin.write(frame.tobytes())

        cap.release()
        process.stdin.close()
        process.wait()
        average_count = total_people / frame_count if frame_count else 0
    else:  # Image
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_counted{ext}"
        ret, frame = cap.read()
        if ret:
            person_coords = get_person_coordinates(model, frame)
            for bbox in person_coords:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

            people_count = len(person_coords)
            text = f"People: {people_count}"
            cv2.putText(
                frame,
                text,
                (x, y),
                font,
                font_scale,
                (0, 0, 0),
                thickness
            )

            cv2.imwrite(output_path, frame)

        cap.release()
        average_count = people_count

    return average_count, output_path
