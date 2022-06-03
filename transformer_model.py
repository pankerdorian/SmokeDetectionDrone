from torchfusion_utils.fp16 import convertToFP16
from torchfusion_utils.initializers import *
from torchfusion_utils.metrics import Accuracy
from torchfusion_utils.models import load_model,save_model

import torch
from torch.autograd import Variable
import matplotlib.pyplot as plt
from torchvision import datasets, transforms, models
from PIL import Image

# ml_model = torch.load('pre_trained_model.pt', map_location=torch.device('cpu'))
ml_model = torch.load('pre_trained_model.pt')
ml_model.eval()
transformer = transforms.Compose([transforms.Resize(225),
                                    transforms.CenterCrop(224),
                                    transforms.ToTensor(),
                                    transforms.Normalize([0.5, 0.5, 0.5],
                                                        [0.5, 0.5, 0.5])])

def predict(img):
    # transformer = ...
    img_processed = transformer(img).unsqueeze(0)
    img_var = Variable(img_processed, requires_grad=False)
    img_var = img_var.cuda()
    # ml_model.eval()
    logp = ml_model(img_var)
    expp = torch.softmax(logp, dim=1)
    confidence, clas = expp.topk(1, dim=1)

    return [clas, confidence.item()]

def main():
    img_path = 'image_99.jpg'  # our-fire
    img = Image.open(img_path).convert('RGB')
    predictions = ['Fire', 'Neutral', 'Smoke']
    predicted_index, confidence = predict(img)
    print(predictions[predicted_index], confidence)

if __name__ == '__main__':
    main()