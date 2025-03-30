import torch.nn as nn

class PolicyNetwork(nn.Module):
    def __init__(self, num_state_vars, num_action_options):
        # Using one-hot encoding (3 values for each player's number of cards, 5 for each player's number of coins)
        # Number of coins can be 0, 1, 2, 3-6, or 7+ (Split based on what actions the player can do)
        super(PolicyNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(num_state_vars, 128),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, num_action_options),
        )

    def forward(self, x):
        return self.fc(x)