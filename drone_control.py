from djitellopy import Tello
import time
import matplotlib.pyplot as plt
import cv2
import threading

# TODO: drone path 
def drone_path():
    tello.takeoff()
    time.sleep(5)
    tello.move_forward(100)
    tello.land()

def get_status(tello):
    status = {
        'battery': tello.get_battery(), 
        'height': tello.get_height(), 
        'speed': f'x: {tello.get_speed_x()} y: {tello.get_speed_y()} z: {tello.get_speed_z()}'
    }
    return status

# TODO:stream on 
def stream_on():
    tello.streamon()  # start UDP stream
    t.start()
    while True:
        frame_obj = tello.get_frame_read()
        frame = frame_obj.frame
        cv2.imshow('frame', frame)
        cv2.waitKey(1)
        if time.time() - start > 60:
            print('stopping after 60 seconds of stream')
            break

def main():
    tello = Tello()
    tello.connect()
    try:
        status = get_status(tello)
        print(status)
    except Exception as e:
        print(f'Exception raised: {e}')
    finally:
        tello.end()



# instruction = ['forward' , 100]
# route = [inst1, inst2, inst3]
# goThroughRoute(route)


# def get_frame(tello):
#     tello.streamon()  # start UDP stream
#     while True:
#         frame_obj = tello.get_frame_read()
#         frame = frame_obj.frame
#         cv2.imshow('frame', frame)
#         cv2.waitKey(1)
#         if time.time() - start > 60:
#             print('stopping after 60 seconds of stream')
#             break


# def flip_drone(tello):
#     tello.takeoff()
#     time.sleep(10)
#     tello.flip_forward()
#     time.sleep(10)
#     tello.flip_forward()
#     tello.land()


# try:
#     tello = Tello()
#     tello.connect()
#     start = time.time()
#     print('start: ' + str(start))
#     print('battery: ' + str(tello.get_battery()))
#     # t = threading.Thread(target=flip_drone, args=[tello])
#     tello.streamon()  # start UDP stream
#     # t.start()
#     while True:
#         frame_obj = tello.get_frame_read()
#         frame = frame_obj.frame
#         cv2.imshow('frame', frame)
#         cv2.waitKey(1)
#         if time.time() - start > 60:
#             print('stopping after 60 seconds of stream')
#             break
#     # t.join()
# except Exception as e:
#     print(f'error: {e}')
# finally:
#     tello.streamoff()
#     end = time.time()
#     print(f'end: {end}')
#     tello.end()


if __name__ == '__main__':
    main()

