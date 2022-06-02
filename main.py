import cv2

def main():
    print(cv2.__version__)
    print('newly added line of code')
    # TODO: control drone
        # TODO: stream on
        # TODO: path (cheack before if current battery is over 20%)
        # TODO: get drone status: hight, battary, velocity
        # TODO: save 2 frames as varibals to send it to > image processing
     
    #  TODO: image processing model 
        # TODO: use 2 frames that u saved before frome the drone 
        # TODO: save the result to a variable 
        # TODO: check where is the interest point 
        # TODO: find the current location from the picture using the known location 

    # TODO: machine learning model
        # TODO: use the saved image and check what the prediction 
        # TODO: save the result
    
    # TODO : classify 
        # TODO: conbine the result and make a choise > there is a fire or smoke ? 
        # our_method * w1 + ml_model * w2 > 0.65 (w1 + w2 = 1)
        # TODO: if the answer is yes, update dataset 
    
    # TODO: update wix 
        # TODO: update drone statuse
        # TODO: update drone event only if the event is new (we need to decide how to realize that we are not getting the same event twice)  

     


if __name__ == '__main__':
    main()
