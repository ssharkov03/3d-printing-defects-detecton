import torch
import torch.nn as nn
import numpy as np
from torchvision import models, transforms


def load_checkpoint(checkpoint):
    model.load_state_dict(checkpoint['state_dict'])


# Model configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = models.alexnet().to(device)
layers_to_unfreeze = 5

for param in model.features[:-layers_to_unfreeze].parameters():
    param.requires_grad = False

num_features = 9216
model.classifier = nn.Sequential(
    nn.Dropout(p=.5),
    nn.Linear(num_features, 2)
)
model = model.to(device)


# Load model
path_to_model = 'alexnet_mixed_good_ds_different_lrs.pth.tar'
load_checkpoint(torch.load(path_to_model, map_location=device))


# Reconfig for cleaner result
model.classifier = nn.Sequential(
    nn.Dropout(p=.5),
    nn.Linear(num_features, 2),
    nn.Softmax(dim=1)
)


# If train needed, add these lines
"""
loss = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(params=[
        {"params": list(model.features.parameters())[-layers_to_unfreeze:], "lr": 1e-7, "weight_decay": 1e-7},
        {"params": list(model.classifier.parameters()), "lr": 1e-6, "weight_decay": 1e-7}
])
"""


# Data transformations for valid/test
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])

data_transforms = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize(600),
        transforms.ToTensor(),
        transforms.Normalize(mean, std)])


# For getting prediction on picture
def get_prediction(img):
    model.eval()
    img = data_transforms(img)
    img = torch.unsqueeze(img, 0)
    img = img.to(device)

    phase = 'test'
    with torch.set_grad_enabled(phase == 'train'):
        outputs = model(img)
        probability_of_no_defects, probability_of_yes_defects = outputs[0]

    if probability_of_yes_defects.item() <= 0.5:
        option = "Minimal defects probability - "
    elif 0.5 < probability_of_yes_defects.item() < 0.65:
        option = "Low defects probability - "
    elif 0.65 <= probability_of_yes_defects.item() <= 0.8:
        option = "ALERT!\nMedium defects probability - "
    else:
        option = "ALERT!\nHigh defects probability - "

    return [option, probability_of_yes_defects.item()]


# For sending images to telegram
def imget(frame, title=None):
    img = transforms.ToPILImage()(frame)
    return img
