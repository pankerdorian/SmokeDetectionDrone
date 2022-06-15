import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import uuid
from PIL import Image
from transformer_model import predict
from smoke_detection import process_frames, system_report
from Wix import Wix
import FireBase
from coordinate_to_GPS import Field, gps_distance
from drone_control import control as drone_controller

HOME_COORDINATES = '31.905399264755708, 34.78181596562009'


def find_smoke_pixel(drone, blocks):
    # np.max(np.nonzero(blocks_of_smoke)[0])
    # 1663
    # np.nonzero(blocks_of_smoke)[1][np.argmax(np.nonzero(blocks_of_smoke)[0])]
    # 1920
    y_indexes, x_indexes = np.nonzero(blocks)
    y = np.max(y_indexes)
    x = x_indexes[np.argmax(y_indexes)]
    # return "25.197148444069278, 55.27437639783683"
    field = Field(h=drone.get_height())
    return field.get_fire_cartesian(y, x)


def main():
    wix = Wix()
    predictions = ['Fire', 'Neutral', 'Smoke']
    route = [
        ['left', 100],
        ['right', 100]
    ]
    controller = drone_controller(route, simulation=True)
    last_gps = (0, 0)
    plt.ion()
    plt.show()
    while True:
        try:
            tello, status, frames = next(controller)
            img = frames[2]
            plt.imshow(img)
            plt.pause(0.001)
            # our model
            blocks_of_smoke = process_frames(frames)
            smoke_detected = 1 if type(blocks_of_smoke) is not type(
                False) and blocks_of_smoke.any() else 0
            # Machine Learning model
            img_for_transformer = img
            if type(img_for_transformer) is np.ndarray:
                img_for_transformer = Image.fromarray(img_for_transformer)
            [predicted_index, conf] = predict(img_for_transformer)

            w1 = 0.1
            w2 = 0.9
            alarm_threshold = 0.5  # (w1 + w2 = 1)

            above_alarm_thresh = (predictions[predicted_index] == 'Smoke' and (
                smoke_detected * w1 + conf * w2 > alarm_threshold))
            is_fire_alarm = predictions[predicted_index] == 'Fire'
            status_data = status
            insert_result = wix.send_to_db(data=status_data, path='status')

            if above_alarm_thresh or is_fire_alarm:
                # don't send the same event twice
                if smoke_detected:
                    gps = find_smoke_pixel(tello, blocks_of_smoke)
                else:
                    gps = HOME_COORDINATES  # TODO: if we can, change to drone coordinates
                if gps_distance(gps, last_gps) < 0.1:
                    continue
                last_gps = gps
                imagePath = f"{uuid.uuid1()}.jpg"
                im = Image.fromarray(img)
                im.save(imagePath)
                download_url = FireBase.add_to_storage(imagePath)
                event_data = {'Location': f'{gps[0]}, {gps[1]}',
                              'Image': download_url, 'Status': 'Waiting'}
                insert_result = wix.send_to_db(data=event_data, path='event')
                print('added event')
                # TODO: if the event was inserted to Wix -> delete image from disk (insert_result.status_code == 201)
        except StopIteration as si:
            print('drone stopped')
            break



if __name__ == '__main__':
    main()
