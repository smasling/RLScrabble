
LETTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
class Tile():
    def __init__(self, multiplier = None):
        super().__init__()
        self.letter = None
        self.multiplier = multiplier
        self.playable = [LETTERS, LETTERS]

    def setLetter(self, letter):
        self.letter = letter

    def set_cross_set(self, direction, new_set):
        self.playable[direction] = new_set