import torch.nn as nn

class PolicyNetwork(nn.Module):
    def __init__(self, numStateVars, numActionOptions):
        # Using one-hot encoding (3 values for each player's number of cards, 5 for each player's number of coins)
    # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
        super(PolicyNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(numStateVars, 128),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, numActionOptions),
        )

    def forward(self, x):
        return self.fc(x)