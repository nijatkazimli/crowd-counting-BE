import cv2
import pandas as pd
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
    x = 10
    y = 20
    if x + text_width > frame_width:
        x = frame_width - text_width - 10
    if y + text_height > frame_height:
        y = frame_height - text_height - 10
        
        


    if total_frames > 1:  # Video
        if output_path is None:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_counted.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

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
            out.write(frame)

        cap.release()
        out.release()
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
