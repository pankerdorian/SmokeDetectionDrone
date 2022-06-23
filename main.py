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
from djitellopy import Tello
from drone_control import control as drone_controller, stop_all_drone_activity, get_status
import threading
import time

HOME_COORDINATES = '31.905399264755708, 34.78181596562009'
HOME_GPS_COORDINATES = (31.905399264755708, 34.78181596562009)


def find_smoke_pixel(drone, blocks):
    # np.max(np.nonzero(blocks_of_smoke)[0])
    # 1663
    # np.nonzero(blocks_of_smoke)[1][np.argmax(np.nonzero(blocks_of_smoke)[0])]
    # 1920
    y_indexes, x_indexes = np.nonzero(blocks)
    y = np.max(y_indexes)
    x = x_indexes[np.argmax(y_indexes)]
    # return "25.197148444069278, 55.27437639783683"
    field = Field(drone_coordinates=HOME_GPS_COORDINATES, h=drone.get_height())
    gps = field.get_fire_cartesian(y, x)
    # with open('gps.txt', 'a') as f:
    #     f.write(f'{gps}\n')
    return HOME_GPS_COORDINATES


directions = {
    'up': 'up',
    'down': 'down',
    'left': 'left',
    'right': 'right',
    'forward': 'forward',
    'back': 'back',
    # stay needs to send change velocity command
    'stay': 'stay'
}
x = 490
barbecue_route = [
    ['up', 100, 'once'],
    ['forward', x],
    ['rotate_right', 80],
    ['stay', 1],
    ['stay', 1],
    ['stay', 1],
    ['rotate_right', 100],
    ['forward', x],
    ['rotate_right', 180]
]
room_route = [
    ['up', 50, 'once'],
    ['forward', 50],
    ['stay', 1],
    ['rotate_right', 90],
    ['rotate_right', 90],
    ['forward', 50],
    ['rotate_right', 180],
]
stay_route = [
    ['up', 100, 'once'],
    ['stay', 1]
]


def use_route(tello, route, index):
    instruction = route[index]
    if len(instruction) == 3:
        direction, x, once = instruction
        route.pop(index)
    else:
        direction, x = instruction
    # keep the same speed (just to send a comand)
    if direction == 'stay':
        tello.set_speed(100)
    elif direction == 'rotate_right':
        tello.rotate_clockwise(x)
    elif direction == 'rotate_left':
        tello.rotate_counter_clockwise(x)
    else:
        tello.move(direction, x)
    time.sleep(1)


def go_home(tello, route, i):
    while i < len(route):
        use_route(tello, route, i)
        i += 1


def main():
    stop = False
    tello = Tello()
    tello.connect()
    # start UDP stream
    tello.streamon()
    frame_obj = tello.get_frame_read()
    brain_thread = threading.Thread(
        target=brain, args=[tello, frame_obj, lambda: stop])
    try:
        time.sleep(5)
        start = time.time()
        print('start: ' + str(start))
        print('battery: ' + str(tello.get_battery()))
        tello.takeoff()
        time.sleep(5)
        i_route = 0
        # route = barbecue_route
        route = stay_route
        number_of_instructions = len(route)
        stop = False
        brain_thread.start()
        while not stop:
            if tello.get_battery() <= 15:
                print('going home')
                go_home(tello, route, i_route)
                stop = True
                break
            r = route[i_route]
            use_route(tello, route, i_route)
            # check if we popped from route ('once' command)
            if r != route[i_route]:
                i_route -= 1
                number_of_instructions -= 1
            i_route = (i_route + 1) % number_of_instructions
    except Exception as exc:
        print(f'error: {exc}')
        stop = True
    finally:
        brain_thread.join()
        tello.streamoff()
        tello.land()
        end = time.time()
        print(f'end: {end}')
        tello.end()


def brain(tello, frame_obj, stop):
    wix = Wix()
    plt.ion()  # make plt interactive
    plt.show()
    predictions = ['Fire', 'Neutral', 'Smoke']
    # (w1 + w2 = 1)
    w1 = 0.15
    w2 = 0.85
    # alarm_threshold = 0.92
    alarm_threshold = 0.5
    last_gps = (0, 0)
    frame_count = 0
    while not stop():
        frames = []
        status = get_status(tello)
        for i in range(3):
            frame = frame_obj.frame
            frames.append(frame)
        frame_count += 1
        print(f'frame number: {frame_count}')
        img = frames[2]
        img_for_transformer = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.imshow(img_for_transformer)
        plt.pause(0.0001)
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
        status_data = status
        insert_result = wix.send_to_db(data=status_data, path='status')
        with open('statuses.txt', 'a') as f:
            f.write(f'{status_data}\n')

        if not (above_alarm_thresh or is_fire_alarm):
            with open('confidence_score.txt', 'a') as f:
                f.write(
                    f'confidence: {predictions[predicted_index]}: {conf}\n')
        if above_alarm_thresh or is_fire_alarm:
            print('event found')
            with open('confidence_score.txt', 'a') as f:
                f.write(f'EVENT: {predictions[predicted_index]}: {conf}\n')
            # don't send the same event twice
            if smoke_detected:
                gps = find_smoke_pixel(tello, blocks_of_smoke)
            else:
                gps = HOME_GPS_COORDINATES  # TODO: if we can, change to drone coordinates
            if gps_distance(gps, last_gps) < 0.1:
                pass
            last_gps = gps
            imagePath = f"{uuid.uuid1()}.jpg"
            im = Image.fromarray(img_for_transformer)
            im.save(imagePath)
            # TODO: start timer for #3
            download_url = FireBase.add_to_storage(imagePath)
            event_data = {'Location': f'{gps[0]}, {gps[1]}',
                          'Image': download_url, 'Status': 'Waiting'}
            insert_result = wix.send_to_db(data=event_data, path='event')
            # TODO: stop timer for #3
            event_data = {'Location': f'{gps[0]}, {gps[1]}',
                          'Image': imagePath, 'Status': 'Waiting'}
            with open('events.txt', 'a') as f:
                f.write(f'{event_data}\n')
            print('added event')
            # TODO: if the event was inserted to Wix -> delete image from disk (insert_result.status_code == 201)


if __name__ == '__main__':
    main()
