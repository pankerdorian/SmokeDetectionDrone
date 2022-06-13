from djitellopy import Tello
import time
import matplotlib.pyplot as plt
import cv2
import threading

class TelloSim:
    def __init__(self, h=9):
        self.battery = 20
        self.height = h
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 20

    def connect(self):
        print('Connected to simulator')
    
    def end(self):
        print('Simulator disconnected')
    
    def get_battery(self):
        self.battery -= 1
        return self.battery

    def get_height(self):
        return self.height

    def get_speed_x(self):
        return self.speed_x

    def get_speed_y(self):
        return self.speed_y
    
    def get_speed_z(self):
        return self.speed_z

    def takeoff(self):
        print('takeoff success!')
    
    def land(self):
        print('Simulator landed safely')

    def move(self, direction, x):
        print(f'moving {x}cm in {direction} direction')


def drone_path(tello, route):
    """route = [['forward', 100], ['right', 10]]"""
    while tello.get_battery() >= 15:
        for direction, x in route:
            tello.move(direction, x)
            time.sleep(1)

def get_status(tello):
    status = {
        'battery': tello.get_battery(), 
        'height': tello.get_height(), 
        'speed': f'x: {tello.get_speed_x()} y: {tello.get_speed_y()} z: {tello.get_speed_z()}'
    }
    return status

# TODO:stream on 
def get_frame(tello):
    frame_obj = tello.get_frame_read() # { 'frame': ACTUAL_FRAME }
    frame = frame_obj.frame
    cv2.imshow('frame', frame)
    cv2.waitKey(1)
    if time.time() - start > 60:
        print('stopping after 60 seconds of stream')
        break


# TODO: fork of the 3 functions as threads
def run(tello):
    # takeoff
    tello.takeoff()
    time.sleep(5)
    # start stream
    # path + status + frame
    # change speed to current speed (avoid landing due to no command)
    # land
    tello.land()
    pass

def main():
    # tello = Tello()
    tello = TelloSim()
    tello.connect()
    try:
        status = get_status(tello)
        print(status)
        # up, down, left, right, forward or back
        route = [
            ['forward', 100],
            ['down', 500],
            ['left', 1],
            ['back', 10],
        ]
        drone_path(tello, route)
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

