import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import uuid
from PIL import Image
from transformer_model import predict
from smoke_detection import alarm, system_report
from Wix import Wix
import FireBase
from coordinate_to_GPS import Field
from drone_control import control as drone_controller

HOME_COORDINATES = '31.905399264755708, 34.78181596562009'


def find_smoke_pixel(blocks):
    # np.max(np.nonzero(blocks_of_smoke)[0])
    # 1663
    # np.nonzero(blocks_of_smoke)[1][np.argmax(np.nonzero(blocks_of_smoke)[0])]
    # 1920
    y_indexes, x_indexes = np.nonzero(blocks)
    y = np.max(y_indexes)
    x = x_indexes[np.argmax(y_indexes)]
    # return "25.197148444069278, 55.27437639783683"
    field = Field(h=9)
    return field.get_fire_cartesian(y, x)


def main():
    wix = Wix()
    predictions = ['Fire', 'Neutral', 'Smoke']
    route = [
        ['left', 100],
        ['right', 100]
    ]
    controller = drone_controller(route, simulation=True)
    while True:
        try:
            status, img = next(controller)
            # our model
            # TODO: refactor alarm to a better name..
            blocks_of_smoke = alarm(img)
            smoke_detected = 1 if blocks_of_smoke and blocks_of_smoke.any() else 0
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
            if above_alarm_thresh or is_fire_alarm:
                # TODO: don't send the same event twice
                imagePath = f"{uuid.uuid1()}.jpg"
                im = Image.fromarray(img)
                im.save(imagePath)
                download_url = FireBase.add_to_storage(imagePath)
                if smoke_detected:
                    gps = find_smoke_pixel(blocks_of_smoke)
                else:
                    gps = HOME_COORDINATES  # TODO: if we can, change to drone coordinates
                event_data = {'Location': gps,
                              'Image': download_url, 'Status': 'Waiting'}
                insert_result = wix.send_to_db(data=event_data, path='event')
                print('added event')
                # TODO: if the event was inserted to Wix -> delete image from disk (insert_result.status_code == 201)
            status_data = status
            insert_result = wix.send_to_db(data=event_data, path='status')
            time.sleep(5)
            break
        except StopIteration as si:
            print('drone stopped')


if __name__ == '__main__':
    main()
