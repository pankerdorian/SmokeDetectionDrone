from Wix import Wix
import time

data = {
	"Location": "31.905399264755708, 34.78181596562009",
	"Image": "https://storage.googleapis.com/firedetectiondrone-9b202.appspot.com/057e051a-efef-11ec-823c-701ce7f437b4.jpg",
	"Status": "Waiting"
}
wix = Wix()
start = time.time()
wix.send_to_db(data, 'event')
print(f'done after {time.time() - start}\n')