import torch

initialStateObj = {
    'A' : 9
    'B' : 2,
    'C' : 2,
    'D' : 4,
    'E' : 12,
    'F' : 2,
    'G' : 3,
    'H' : 2,
    'I' : 8,
    'J' : 1,
    'K' : 1,
    'L' : 4,
    'M' : 2,
    'N' : 6,
    'O' : 8,
    'P' : 2,
    'Q' : 1,
    'R' : 6,
    'S' : 4,
    'T' : 6,
    'U' : 4,
    'V' : 2,
    'W' : 2,
    'X' : 1,
    'Y' : 2,
    'Z' : 1,
    '?' : 2,
    'First Letter Remaining': None,
    'Second Letter Remaining': None,
    'Third Letter Remaining': None,
    'Fourth Letter Remaining': None,
    'Fifth Letter Remaining': None,
    'Sixth Letter Remaining': None,
    'Seventh Letter Remaining': None,
    'Your Score': 0,
    'Opponents Score': 0,
    'Score Differential' : 0,
    'Move Score': None,
    '(0,0)': None,
    '(0,1)': None,
    '(0,2)': None,
    # ...
    '(14,13)': None,
    '(14, 14)': None,
}

#features = 26 (letters) + 11 (misc) + 225 (board) = 252

initState = torch.zeros(252)
initWeights = torch.rand.int(252)