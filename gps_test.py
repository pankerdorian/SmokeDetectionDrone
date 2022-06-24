import numpy as np
import cv2
from smoke_detection import process_frames
from coordinate_to_GPS import Field, gps_distance

HOME_GPS_COORDINATES = (31.905399264755708, 34.78181596562009)

def find_smoke_pixel(blocks):
    # get lowest smoke pixel
    y_indexes, x_indexes = np.nonzero(blocks)
    y = np.max(y_indexes)
    x = x_indexes[np.argmax(y_indexes)]
    # find its GPS coordinates
    field = Field(drone_coordinates=HOME_GPS_COORDINATES, h=1.9)
    print(f'coordinates {y, x}')
    gps = field.get_fire_cartesian(y, x)
    return gps


frame1 = cv2.imread('fbf5490a-efee-11ec-b1f1-701ce7f437b4.jpg')
frame2 = cv2.imread('fdca1f90-efee-11ec-bd8c-701ce7f437b4.jpg')
frame3 = cv2.imread('ff5ea618-efee-11ec-87c1-701ce7f437b4.jpg')

blocks = process_frames([frame1, frame2, frame3])
print(find_smoke_pixel(blocks))