import numpy as np
import torch 
import torch.nn as nn

from Metrics import Metrics

class BasicClassifier(nn.Module):
    def __init__(self,num_classes) -> None:
        self.num_classes = num_classes
        self.metric = Metrics()
        super(BasicClassifier, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1,64,kernel_size=7),
            nn.ReLU(inplace=True),
            nn.Conv2d(64,128,kernel_size=11),
            nn.ReLU(inplace=True),
            nn.Conv2d(128,182,kernel_size=3),
            nn.ReLU(inplace=True),
            nn.Conv2d(182,256,kernel_size=5),
        )
        self.classifier = nn.Sequential(
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096,2048),
            nn.ReLU(inplace=True),
            nn.Linear(2048,1024),
            nn.ReLU(inplace=True),
            nn.Linear(1024,num_classes),
            nn.Softmax(dim=0),            
        )
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
