import numpy as np
import cv2
from PIL import Image
import time
from transformer_model import predict
from smoke_detection import process_frames


predictions = ['Fire', 'Neutral', 'Smoke']
w1 = 0.15
w2 = 0.85
alarm_threshold = 0.5
frame_count = 2
alert_count = 0
first_alert = -1
last_alert = -1
vid = cv2.VideoCapture('./vids/station3.mp4')
success, image1 = vid.read()
success, image2 = vid.read()
# get first 2 frames from vid (first one twice because we pop(0) in every iteration)
frames = [image1, image1, image2]

success, frame = vid.read()
while success:
    start_time = time.time()
    # add the frame
    frames.append(frame)
    frames.pop(0)
    img = frames[2]
    img_for_transformer = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # our model
    blocks_of_smoke = process_frames(frames)
    smoke_detected = 1 if type(blocks_of_smoke) is not type(
        False) and blocks_of_smoke.any() else 0
    # Machine Learning model
    if type(img_for_transformer) is np.ndarray:
        img_for_transformer = Image.fromarray(img_for_transformer)
    [predicted_index, conf] = predict(img_for_transformer)

    above_alarm_thresh = (predictions[predicted_index] == 'Smoke' and (
        smoke_detected * w1 + conf * w2 > alarm_threshold))
    is_fire_alarm = predictions[predicted_index] == 'Fire'

    if above_alarm_thresh or is_fire_alarm:
        alert_count += 1
        if first_alert == -1:
            first_alert = frame_count
        last_alert = frame_count
    print(f'processed frame {frame_count} in {time.time() - start_time} seconds')
    frame_count += 1
    success, frame = vid.read()

vid.release()
print('done!')
print(f'num_frames: {frame_count} \nnum_alerts: {alert_count} \nfirst_alert: {first_alert} \nlast_alert: {last_alert}')
