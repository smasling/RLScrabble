from copy import deepcopy
from Gaddag import Dictionary, DELIMITER, Arc
from utils import *
import Tile
import string

LETTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

class Board():
    def __init__(self):
        super().__init__()
        self.board = b()

    def __str__(self):
        board_string = ""
        for i in range(len(self.board)):
            row = (self.square((i, j)).letter for j in range(len(self.board)))
            row_string = "  ".join(tile if tile else "-" for tile in row)
            board_string = board_string + row_string + "\n"
        return board_string

    def square(self, coord):
        """gets the square on the given coordinate, return None if out of bounds"""
        row, col = coord
        if row < 0 or row >= len(self.board):
            return None
        if col < 0 or col >= len(self.board):
            return None
        return self.board[row][col]

    def scorePlay(self, coord, word, direction):
        def scoreOppo(coord, letter, direction):
            multiplier = 1
            score = 0
            left = self.offset(coord, direction, -1)
            right = self.offset(coord, direction, 1)
            leftSquare = self.square(left)
            rightSquare = self.square(right)
            if (not leftSquare or not leftSquare.letter) and (not rightSquare or not rightSquare.letter):
                return score
            tile = self.square(coord)
            if not tile.letter:
                if tile.multiplier == "TW":
                    multiplier *= 3
                elif tile.multiplier == "DW":
                    multiplier *=2
                elif tile.multiplier == "TL":
                    score += points[letter] * 3
                elif tile.multiplier == "DL":
                    score += points[letter] * 2
                else:
                    score += points[letter]
            else:
                score += points[letter]
            while leftSquare and leftSquare.letter:
                score += points[leftSquare.letter]
                left = self.offset(left, direction, -1)
                leftSquare = self.square(left)
            while rightSquare and rightSquare.letter:
                score += points[rightSquare.letter]
                right = self.offset(right, direction, 1)
                rightSquare = self.square(right)
            return score
        lettersUsed = 0
        otherDirection = 0 if direction == 1 else 1
        oppoScore = 0
        directScore = 0
        multiplier = 1
        tile = self.square(coord)
        while len(word) > 0:
            if not tile:
                print(self.__str__())
            if tile.letter:
                directScore += points[word[0]]
            else:
                lettersUsed += 1
                oppoScore += scoreOppo(coord, word[0], otherDirection)
                if tile.multiplier == "TW":
                    multiplier *= 3
                    directScore += points[word[0]]
                elif tile.multiplier == "DW":
                    multiplier *=2
                    directScore += points[word[0]]
                elif tile.multiplier == "TL":
                    directScore += points[word[0]] * 3
                elif tile.multiplier == "DL":
                    directScore += points[word[0]] * 2
                else:
                    directScore += points[word[0]]
            coord = self.offset(coord, direction, 1)
            tile = self.square(coord)
            word = word[1:]
        directScore *= multiplier
        return directScore + oppoScore + (50 if lettersUsed == 7 else 0)

    def generate_moves(self, anchor, direction, rack, dictionary, tile_set, anchors_used):
        """generate all possible moves from a given anchor with the current rack"""

        plays = []

        def gen(pos_, word_, rack_, arc_, new_tiles_, wild_cards_):
            rack_ = deepcopy(rack_)
            coord = self.offset(anchor, direction, pos_)
            tile = self.square(coord).letter
            if tile:
                new_tiles_ = deepcopy(new_tiles_)
                go_on(pos_, tile, word_, rack_, arc_.get_next(tile), arc_, new_tiles_, wild_cards_)
            elif rack_:
                other_direction = 1 if direction == 0 else 0
                for letter_ in (x for x in set(rack_) if x in self.square(coord).playable[other_direction]):
                    tmp_rack_ = deepcopy(rack_)
                    tmp_rack_.remove(letter_)
                    tmp_new_tiles_ = deepcopy(new_tiles_)
                    tmp_new_tiles_.append(pos_)
                    go_on(pos_, letter_, word_, tmp_rack_, arc_.get_next(letter_), arc_, tmp_new_tiles_, wild_cards_)
                if "?" in rack_:
                    for letter_ in (x for x in LETTERS if
                                    x in self.square(coord).playable[other_direction]):
                        tmp_rack_ = deepcopy(rack_)
                        tmp_rack_.remove("?")
                        tmp_new_tiles_ = deepcopy(new_tiles_)
                        tmp_new_tiles_.append(pos_)
                        tmp_wild_cards_ = deepcopy(wild_cards_)
                        tmp_wild_cards_.append(pos_)
                        next_arc = arc_.get_next(letter_)
                        go_on(pos_, letter_, word_, tmp_rack_, next_arc, arc_, tmp_new_tiles_, tmp_wild_cards_)


        def go_on(pos_, char_, word_, rack_, new_arc_, old_arc_, new_tiles_, wild_cards_):
            directly_left = self.offset(anchor, direction, pos_ - 1)
            directly_left_square = self.square(directly_left)
            directly_right = self.offset(anchor, direction, pos_ + 1)
            directly_right_square = self.square(directly_right)
            right_side = self.offset(anchor, direction, 1)
            right_side_square = self.square(right_side)

            if pos_ <= 0:
                word_ = char_ + word_
                left_good = not directly_left_square or not directly_left_square.letter
                right_good = not right_side_square or not right_side_square.letter
                if char_ in old_arc_.letter_set and left_good and right_good and new_tiles_:
                    temp_word = word_[:]
                    # print(wild_cards_, word_)
                    for i in wild_cards_:
                        i = i - pos_
                        temp_word = temp_word[:i] + temp_word[i].lower() + temp_word[i+1:]
                    plays.append((temp_word, self.scorePlay(self.offset(anchor, direction, pos_), temp_word, direction), self.offset(anchor, direction, pos_), direction))
                if new_arc_:
                    if directly_left_square and directly_left not in anchors_used:
                        gen(pos_ - 1, word_, rack_, new_arc_, new_tiles_, wild_cards_)
                    new_arc_ = new_arc_.get_next(DELIMITER)
                    if new_arc_ and left_good and right_side_square:
                        gen(1, word_, rack_, new_arc_, new_tiles_, wild_cards_)
            else:
                word_ = word_ + char_
                right_good = not directly_right_square or not directly_right_square.letter
                if char_ in old_arc_.letter_set and right_good and new_tiles_:
                    left_most = pos_ - len(word_) + 1
                    temp_word = word_[:]
                    for i in wild_cards_:
                        index = i - left_most
                        temp_word = temp_word[:index] + temp_word[index].lower() + temp_word[index+1:]

                    plays.append((temp_word, self.scorePlay(self.offset(anchor, direction, left_most), temp_word, direction), self.offset(anchor, direction, left_most), direction))
                if new_arc_ and directly_right_square:
                    gen(pos_ + 1, word_, rack_, new_arc_, new_tiles_, wild_cards_)

        initial_arc = Arc("", dictionary.root)
        gen(0, "", deepcopy(rack), initial_arc, [], [])
        # print(plays)
        return plays

    def update_cross_set(self, start_coordinate, direction, dictionary):
        """update cross sets affected by this coordinate"""

        def __clear_cross_sets(start_coordinate_, direction_):
            right_most_square = self.fast_forward(start_coordinate_, direction_, 1)
            right_square_ = self.offset(right_most_square, direction_, 1)
            if self.square(right_square_):
                self.square(right_square_).set_cross_set(direction_, {})
            left_most_square = self.fast_forward(start_coordinate_, direction_, -1)
            left_square_ = self.offset(left_most_square, direction_, -1)
            if self.square(left_square_):
                self.square(left_square_).set_cross_set(direction_, {})

        def __check_candidate(coordinate_, candidate_, direction_, step):
            last_arc_ = candidate_
            state_ = candidate_.destination
            next_square_ = self.offset(coordinate_, direction_, step)
            while self.square(next_square_) and self.square(next_square_).letter:
                coordinate_ = next_square_
                tile_ = self.square(coordinate_).letter.upper()
                last_arc_ = state_.arcs[tile_] if tile_ in state_.arcs else None
                if not last_arc_:
                    return False
                state_ = last_arc_.destination
                next_square_ = self.offset(coordinate_, direction_, step)
            return self.square(coordinate_).letter.upper() in last_arc_.letter_set

        if not self.square(start_coordinate) or not self.square(start_coordinate).letter:
            return  # do not do anything if this square is out of bounds or empty
        end_coordinate = self.fast_forward(start_coordinate, direction, 1)

        # traverse the dictionary in reverse order of the word
        coordinate = end_coordinate
        last_state = dictionary.root
        state = last_state.get_next(self.square(coordinate).letter.upper())
        next_square = self.offset(coordinate, direction, -1)
        while self.square(next_square) and self.square(next_square).letter:
            coordinate = next_square
            last_state = state  # this saves the previous state before incrementing
            state = state.get_next(self.square(coordinate).letter)
            if not state:  # if non-words are found existing on the board
                __clear_cross_sets(start_coordinate, direction)
                return
            next_square = self.offset(coordinate, direction, -1)

        # now that we're at the head of the word
        right_square = self.offset(end_coordinate, direction, 1)
        left_square = self.offset(coordinate, direction, -1)

        # check special case where there is a square with tiles on both sides
        left_of_left = self.offset(left_square, direction, -1)
        right_of_right = self.offset(right_square, direction, 1)

        if self.square(left_of_left) and self.square(left_of_left).letter:
            candidates = (arc for arc in state if arc.char != "#")
            cross_set = set(
                candidate.char for candidate in candidates if __check_candidate(left_square, candidate, direction, -1))
            self.square(left_square).set_cross_set(direction, cross_set)
        elif self.square(left_square):
            cross_set = last_state.get_arc(self.square(coordinate).letter.upper()).letter_set
            self.square(left_square).set_cross_set(direction, cross_set)

        if self.square(right_of_right) and self.square(right_of_right).letter:
            end_state = state.get_next(DELIMITER)
            candidates = (arc for arc in end_state if arc != "#") if end_state else {}
            cross_set = set(
                candidate.char for candidate in candidates if __check_candidate(right_square, candidate, direction, 1))
            self.square(right_square).set_cross_set(direction, cross_set)
        elif self.square(right_square):
            end_arc = state.get_arc(DELIMITER)
            cross_set = end_arc.letter_set if end_arc else {}
            self.square(right_square).set_cross_set(direction, cross_set)

    @staticmethod
    def offset(coordinate, direction, offset):
        if direction == 0:
            new_coordinate = coordinate[0], coordinate[1] + offset
        elif direction == 1:
            new_coordinate = coordinate[0] + offset, coordinate[1]
        else:
            raise TypeError("invalid direction specified: {}".format(direction))
        return new_coordinate

    def fast_forward(self, start_coordinate, direction, step):
        """fast forward the coordinate to the last letter in the word"""
        coordinate = start_coordinate
        next_coordinate = self.offset(start_coordinate, direction, step)
        while self.square(next_coordinate) and self.square(next_coordinate).letter:
            coordinate = next_coordinate
            next_coordinate = self.offset(coordinate, direction, step)
        return coordinate

    def place_word(self, start_coordinate, word, direction):
        """puts a word on the board"""

        end_coordinate = self.offset(start_coordinate, direction, len(word))
        if any(index > len(self.board) for index in end_coordinate):
            raise errors.IllegalMoveError("The length of word is out of bounds of the board")

        coordinate = start_coordinate
        offset = 0
        lettersUsed = []
        for char in word:
            sq = self.square(coordinate)
            if not sq.letter:
                lettersUsed.append(char)
                sq.letter = char
            offset = offset + 1
            coordinate = self.offset(start_coordinate, direction, offset)
        return lettersUsed

    def get_letters_used(self, start_coordinate, word, direction):
        """puts a word on the board"""

        end_coordinate = self.offset(start_coordinate, direction, len(word))
        if any(index > len(self.board) for index in end_coordinate):
            raise errors.IllegalMoveError("The length of word is out of bounds of the board")

        coordinate = start_coordinate
        offset = 0
        lettersUsed = []
        for char in word:
            sq = self.square(coordinate)
            if not sq.letter:
                lettersUsed.append(char)
            offset = offset + 1
            coordinate = self.offset(start_coordinate, direction, offset)
        return lettersUsed

    def find_best_moves(self, rack, direction, dictionary, tile_set):

        anchors_used = []
        moves = []
        other_direction = 0 if direction == 1 else 1

        def is_anchor(coordinate_):
            right = self.offset(coordinate_, direction, 1)
            above = self.offset(coordinate_, other_direction, -1)
            below = self.offset(coordinate_, other_direction, 1)
            cross_squares = (self.square(block) for block in [above, below])
            if not self.square(coordinate_).letter:
                return any(square and square.letter for square in cross_squares)
            return not self.square(right) or not self.square(right).letter

        corner = (0, 0)
        for i in range(len(self.board)):
            left_most = self.offset(corner, other_direction, i)
            for j in range(len(self.board)):
                current = self.offset(left_most, direction, j)
                if is_anchor(current):
                    moves.extend(self.generate_moves(current, direction, rack, dictionary, tile_set, anchors_used))
                    anchors_used.append(current)
        return moves



# a = Board()

# print(a.scorePlay((7,7), "BUNNY", 0))
# a.place_word((7,7), "BUNNY", 0)
# print(a.scorePlay((8, 6), "HAH", 0))
# a.place_word((8,6), "HAH", 0)
# a.place_word((10, 6), "ED", 0)
# print(a.scorePlay((9,5), "ZAL", 0))
# print(a.scorePlay((7,0), "AIRLiNE", 1))
# print(a)


# print(a.generate_moves((7,7), 0, list("ASLESFA"), Dictionary.load_from_pickle('dictionary.p'), BAG, {}))
