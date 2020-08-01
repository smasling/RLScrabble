import torch
import torch.nn as nn
from tqdm import tqdm


class Scrabbler(nn.Module):
    def __init__(self, input_dim, hidden_dims):
        super(Scrabbler, self).__init__()
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.board_size = 15
        self.rack_size = 27
        self.bag_size = 86

        #output size is 144
        self.board_cnn = nn.Sequential(
            nn.Conv2d(2, 2, 2),
            nn.BatchNorm2d(2),
            nn.Conv2d(2, 2, 2),
            nn.BatchNorm1d(2),
            nn.Conv2d(2, 1, 2),
            nn.Flatten()
        )
        self.rack_dn = nn.Sequential(
            nn.Linear(self.rack_size, self.rack_size),
            nn.ReLU(),
            nn.Linear(self.rack_size, 1),
            nn.ReLU()
        )
        self.bag_dn = nn.Sequential(
            nn.Linear(self.bag_size, self.bag_size/2),
            nn.ReLU(),
            nn.Linear(self.bag_size/2, self.bag_size/4),
            nn.ReLU(),
            nn.Linear(self.bag_size/4, 7),
            nn.ReLU()
        )

        self.out_nn = nn.Sequential(
            nn.Linear(self.input_dim, self.hidden_dims[0]),
            nn.ReLU(),
            nn.Linear(self.hidden_dims[0], self.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(self.hidden_dims[1], self.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(self.hidden_dims[2], 1)
        )
    def forward(self, x):
        board = self.board_cnn(x['board'])
        rack = self.rack_dn(x['rack'])
        bag = self.bag_dn(x['bag'])
        out = torch.cat((board, rack, bag, x['score']), 0)
        return self.out_nn(out)



def main():
    board = torch.tensor([[[[0,0] for i in range(15)] for j in range(15)]], dtype=torch.float).reshape(1, 2, 15, 15)
    # loss = nn.BCELoss()
    # model = Scrabbler(154, [154, 77, 10])
    print(board_cnn(board).shape)


if __name__ == "__main__":
    main()