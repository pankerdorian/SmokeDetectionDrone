import cv2
import os
import numpy as np
from PIL import Image
from transformer_model import predict
from smoke_detection import alarm, system_report
from Wix import Wix
import FireBase
from coordinare_to_GPS import get_fire_cartesian

def main():
    wix = Wix()
    predictions = ['Fire', 'Neutral', 'Smoke']
    # TODO: control drone
        # TODO: stream on
        # TODO: path (cheack before if current battery is over 20%)
        # TODO: get drone status: hight, battary, velocity
        # TODO: save 2 frames as varibals to send it to > image processing
     
    # TODO: image processing model
        # TODO: use 2 frames that u saved before frome the drone 
    imagePath = "120.jpg"
    img = cv2.imread(imagePath)
    imagePath = "121.jpg"
    alarm(img)
    img = cv2.imread(imagePath)
    alarm(img)

    imagePath = "122.jpg"
    img = cv2.imread(imagePath)
        # TODO: save the result to a variable
    smoke_detected = 1 if alarm(img) else 0
    print('done!')
        # TODO: check where is the interest point 
        # TODO: find the current location from the picture using the known location
     

    # TODO: machine learning model
        # TODO: use the saved image and check what the prediction
        # TODO: save the result
    img_for_transformer = img
    if type(img_for_transformer) is np.ndarray:
        img_for_transformer = Image.fromarray(img_for_transformer)
    [predicted_index, conf] = predict(img_for_transformer)

    
    # TODO : classify 
        # TODO: conbine the result and make a choise > there is a fire or smoke ? 
    w1 = 0.1
    w2 = 0.9
    alarm_threshold = 0.5 # (w1 + w2 = 1)
    # TODO: update wix 
        # TODO: update drone statuse
        # TODO: update drone event only if the event is new (we need to decide how to realize that we are not getting the same event twice)  
    above_alarm_thresh = (predictions[predicted_index] == 'Smoke' and (smoke_detected * w1 + conf * w2 > alarm_threshold))
    is_fire_alarm = predictions[predicted_index] == 'Fire'
    if above_alarm_thresh or is_fire_alarm:
        download_url = FireBase.add_to_storage(imagePath)
        event_data = {'Location': "25.197148444069278, 55.27437639783683", 'Image': download_url, 'Status': 'Waiting'}
        event_path = 'event'
        insert_result = wix.send_to_db(data=event_data, path=event_path)
        print('added event')
        # TODO: check if the event was inserted to Wix -> delete image from disk
    
   

if __name__ == '__main__':
    main()
