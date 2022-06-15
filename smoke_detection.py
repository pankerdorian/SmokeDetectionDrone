import numpy as np
from skimage import feature
import cv2
import os
import matplotlib.pyplot as plt
from PIL import Image
import base64
from Wix import Wix
import threading

import timer_dec


def motion_detection(frame_sequence):
    g1 = cv2.cvtColor(frame_sequence[0], cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(frame_sequence[1], cv2.COLOR_BGR2GRAY)
    mask = cv2.absdiff(g1, g2)
    mask = cv2.inRange(mask, 5, 256, dst=mask)
    return mask


def get_gray_condition_mask(frame):
    """
    1 ; if max(r,g,b) - min(r,g,b) < uc1\n
    0 ; else\n
    :rtype: np.array
    """
    temp1 = np.copy(frame)
    temp2 = np.copy(frame)
    maximum = max_of_3_arrays(temp1[:, :, 0], temp1[:, :, 1], temp1[:, :, 2])
    minimum = min_of_3_arrays(temp2[:, :, 0], temp2[:, :, 1], temp2[:, :, 2])
    diff = maximum - minimum
    uc1 = 30.70
    mask = cv2.inRange(diff, 0, uc1)
    return mask


def get_dark_color_condition_mask(frame):
    """
    1 ; if (r+g+b)/3 > uc2\n
    0 ; else\n
    :rtype: np.array
    """
    uc2 = 89.04
    t1 = np.copy(frame)
    avg = np.average(t1, axis=2)
    mask = cv2.inRange(avg, uc2, 256)
    return mask


def color_detection(after_motion_mask_frame):
    cr = get_gray_condition_mask(after_motion_mask_frame)
    cp = get_dark_color_condition_mask(after_motion_mask_frame)
    mask = cv2.bitwise_and(cr, cp)
    return mask


def max_of_3_arrays(arr1, arr2, arr3):
    return np.maximum(np.maximum(arr1, arr2), arr3)


def min_of_3_arrays(arr1, arr2, arr3):
    return np.minimum(np.minimum(arr1, arr2), arr3)


def get_lbp_hist(img, p, r, method, num_bins=False):
    lbp = feature.local_binary_pattern(img, p, r, method=method)
    if not num_bins:
        num_bins = np.unique(lbp).shape[0]
    lbp[np.isnan(lbp)] = -1
    h = np.histogram(lbp, bins=num_bins)[0]
    return h


def texture_detection(after_color_frame):
    # TODO: use gaussian filter
    H81 = get_lbp_hist(after_color_frame, 8, 1, 'default', num_bins=256)
    log_HV81 = get_lbp_hist(after_color_frame, 8, 1, 'var')
    H825 = get_lbp_hist(after_color_frame, 8, 2.5, 'default')
    log_HV825 = np.log(get_lbp_hist(after_color_frame, 8, 2.5, 'var'))
    m = np.mean(after_color_frame)
    s = np.std(after_color_frame)
    return H81


def find_relevant_blocks(mask, block_size):
    """:returns blocks location"""
    n, m = block_size
    blocks = np.zeros(shape=mask.shape)
    N = (mask.shape[0] // n) + 2
    M = (mask.shape[1] // m) + 2
    for i in range(N):
        for j in range(M):
            blocks[i * n: n * (i + 1), j * m: m * (j + 1)] = int(
                np.sum(mask[i * n: n * (i + 1), j * m: m * (j + 1)]) > (n * m / 2) * 255)
    return blocks


def centroid_of_blocks(blks):
    avg_x = np.average(np.nonzero(blks)[1])
    avg_y = np.average(np.nonzero(blks)[0])
    return avg_x, avg_y


def draw_centroid(after_blocks_mask, avg_x, avg_y, color=(255, 0, 0)):
    """after_blocks_mask = cv2.bitwise_and(img, img, mask=np.array(blks, dtype='uint8'))"""
    drawing = cv2.circle(
        after_blocks_mask,
        (int(avg_x), int(avg_y)),
        5, color, -1)
    return drawing


def draw_all_centroids(i, b, reg, color=(255, 0, 0)):
    """i: image, b: blocks, reg: regions"""
    after_blocks_mask = cv2.bitwise_and(i, i, mask=np.array(b, dtype='uint8'))
    for r in reg:
        after_blocks_mask = draw_centroid(after_blocks_mask, r['centroid'][0], r['centroid'][1], color)
    return after_blocks_mask


def get_all_regions(image_shape, contours):
    # https://learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
    centroids = []
    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)
        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cent = {
            "region": cv2.drawContours(np.zeros(image_shape, dtype='uint8'), [c], 0, (255, 0, 255), -1),
            "centroid": [cX, cY]
        }
        centroids.append(cent)
    return centroids


def get_prev_region_index(prev, curr):
    max_shared_bits = -1
    max_index = -1
    for i in range(len(prev)):
        shared_bits = cv2.bitwise_and(curr['region'], prev[i]['region'])
        # count the number of non zero pixels
        count = len(np.nonzero(shared_bits)[0])
        if count >= max_shared_bits:
            max_shared_bits = count
            max_index = i
    return max_index


def movement_direction(prev_regions, current_regions):
    # VERY SLOW ~30 SEC
    count_upward_movement = 0
    for a in current_regions:
        max_shared_bits_index = get_prev_region_index(prev_regions, a)
        # check centroid
        prev_y = prev_regions[max_shared_bits_index]['centroid'][1]
        current_y = a['centroid'][1]
        if current_y <= prev_y:
            count_upward_movement += 1
    return len(current_regions) // 2 <= count_upward_movement


def region_grow(regions, regions2):
    # VERY SLOW ~30 SEC
    count_grow = 0
    for a in regions2:
        max_index = get_prev_region_index(regions, a)
        # check growth
        prev_non_zeros = np.nonzero(regions[max_index]['region'])
        current_non_zeros = np.nonzero(a['region'])
        if len(prev_non_zeros[0]) <= len(current_non_zeros[0]):
            count_grow += 1
    return len(regions2) // 2 <= count_grow

@timer_dec.timer
def process_frames(frames, block_size=(64, 64)):
    # get video frames
    img = frames[0]
    img2 = frames[1]
    img3 = frames[2]
    # detect motion
    sequence = [img, img2]
    sequence2 = [img2, img3]
    motion_mask = motion_detection(sequence)
    motion_mask2 = motion_detection(sequence2)
    after_motion = cv2.bitwise_and(img2, img2, mask=motion_mask)
    after_motion2 = cv2.bitwise_and(img3, img3, mask=motion_mask2)
    # mask by smoke color
    mask = color_detection(after_motion)
    mask2 = color_detection(after_motion2)
    # get mask blocks ( > 50%)
    blocks = find_relevant_blocks(mask, block_size=block_size)
    blocks2 = find_relevant_blocks(mask2, block_size=block_size)
    union_of_blocks = cv2.bitwise_or(blocks, blocks2)
    if np.count_nonzero(blocks2) <= 0:
        return False
    # union of blocks if intersection is not empty
    if np.count_nonzero(cv2.bitwise_and(blocks, blocks2)) > 0:
        blocks2 = union_of_blocks
    b_contours, hierarchy = cv2.findContours(np.array(blocks, dtype='uint8'),
                                             cv2.RETR_TREE,
                                             cv2.CHAIN_APPROX_SIMPLE)
    b2_contours, hierarchy2 = cv2.findContours(np.array(blocks2, dtype='uint8'),
                                               cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
    previous_regions = get_all_regions(img2.shape, b_contours)
    current_regions = get_all_regions(img3.shape, b2_contours)
    # check centroid` upward motion
    if len(previous_regions) == 0 or len(current_regions) == 0:
        # could also be True, we expect to recognize the change in the next frame/iteration
        return False
    # e = movement_direction(previous_regions, current_regions)
    e = threading.Thread(target=movement_direction, args=[previous_regions, current_regions])
    e.start()
    # check grow
    r = region_grow(previous_regions, current_regions)
    e.join()
    if r and e:
        return blocks2
    else:
        return False
    # color_filtered = cv2.bitwise_and(img, img, mask=mask)
    # gray = cv2.cvtColor(color_filtered, cv2.COLOR_BGR2GRAY)
    # hist = texture_detection(gray)
    # plt.bar(np.arange(hist.shape[0]), hist)
    # plt.show()

# @timer_dec.timer
def system_report(video_capture):
    success, frame = video_capture.read()
    block_size = (32, 32)
    frame_counter = 1
    num_alerts = 0
    first_alert = -1
    last_alert = -1
    while success:
        # if frame_counter > 50:
          #  break
        if alarm(frame, block_size=block_size):
            if first_alert < 0:
                first_alert = frame_counter
            last_alert = frame_counter
            num_alerts += 1
        success, frame = video_capture.read()
        frame_counter += 1
    return {'block_size': block_size,
            'num_frames': frame_counter,
            'num_alerts': num_alerts,
            'first_alert': first_alert,
            'last_alert': last_alert}


if __name__ == "__main__":
    wix = Wix()
    with open('data/720.jpg', 'rb') as f:
        img = f.read()
        img_binary = base64.b64encode(img)
    event_data = {'Location': "30, 10", 'Image': img_binary, 'Status': 'Waiting'}
    event_path = 'event'
    insert_result = wix.send_to_db(data=event_data, path=event_path)
    print(insert_result.text)
    # vid_path = os.path.join('.', 'video', '3.mp4')
    # vidcap = cv2.VideoCapture(vid_path)
    # report = system_report(vidcap)
    # print(report)
    # vidcap.release()
    # print('done!')
