
import torch
import torch.nn as nn

class AlphaDiscoveryModel(nn.Module):

    def __init__(self,input_size,hidden=64):

        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_size,hidden),
            nn.ReLU(),
            nn.Linear(hidden,hidden),
            nn.ReLU(),
            nn.Linear(hidden,1)
        )

    def forward(self,x):

        return self.net(x)
