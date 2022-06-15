from djitellopy import Tello
import time
import matplotlib.pyplot as plt
import cv2
import threading


class Frame:
    def __init__(self):
        setattr(self, 'frame', None)


class TelloSim:
    def __init__(self, h=3):
        self.battery = 100
        self.height = h
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 20
        self.stream_on = False
        self.frame_index = 0
        self.frames = ['30.jpg', '31.jpg', '32.jpg']
        self.frame_obj = Frame()

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

    def get_frame_read(self):
        if not self.stream_on:
            raise Exception("stream is not on")
        i = self.frame_index
        self.frame_obj.frame = cv2.imread(self.frames[i])
        self.frame_index = (self.frame_index + 1) % 3
        return self.frame_obj

    def streamon(self):
        self.stream_on = True
        print('started stream')

    def streamoff(self):
        self.stream_on = False
        print('ended stream')

    def takeoff(self):
        print('takeoff success!')

    def land(self):
        print('Simulator landed safely')

    def move(self, direction, x):
        print(f'moving {x}cm in {direction} direction')


def drone_path(tello, route):
    """route = [['forward', 100], ['right', 10]]"""
    global stop_all
    while tello.get_battery() >= 15:
        if stop_all:
            print('stoping route')
            break
        for direction, x in route:
            tello.move(direction, x)
            time.sleep(1)


def get_status(tello):
    status = {
        'Battery': tello.get_battery(),
        'Height': tello.get_height(),
        'Speed': f'x: {tello.get_speed_x()} y: {tello.get_speed_y()} z: {tello.get_speed_z()}'
    }
    return status


def get_frame(tello):
    frame_obj = tello.get_frame_read()
    frame = frame_obj.frame
    return frame


stop_all = False
def stop_all_drone_activity():
    global stop_all
    stop_all = True


def control(route, simulation=False):
    try:
        if simulation:
            tello = TelloSim()
        else:
            tello = Tello()
        global stop_all
        stop_all = False
        tello.connect()
        start = time.time()
        print('start: ' + str(start))
        print('battery: ' + str(tello.get_battery()))
        tello.takeoff()
        # start UDP stream
        tello.streamon()
        path_thread = threading.Thread(target=drone_path, args=[tello, route])
        path_thread.start()
        while True:
            frames = []
            status = get_status(tello)
            for i in range(3):
                frame_obj = tello.get_frame_read()
                frame = frame_obj.frame
                frames.append(frame)
            yield tello, status, frames
            if time.time() - start > 60 or tello.get_battery() <= 15:
                print('stopping')
                break
    except Exception as e:
        print(f'error: {e}')
    finally:
        stop_all_drone_activity()
        path_thread.join()
        tello.streamoff()
        tello.land()
        end = time.time()
        print(f'end: {end}')
        tello.end()


if __name__ == '__main__':
    route = [
        ['left', 100],
        ['right', 100]
    ]
    controller = control(route)
    try:
        while True:
            status, frame = next(controller)
            print(status)
            # break
    except StopIteration as si:
        print('drone stopped')
