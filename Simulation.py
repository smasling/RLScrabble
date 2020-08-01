import copy
import numpy as np
from Game import Game
import time
import threading
import json

counter = 0

def saveExample(state, lock):
    lock.acquire()
    with open('examples.json', 'r') as f:
        config = json.load(f)
    if len(config["examples"]) == 0:
        config["examples"] = [state]
    else:
        config["examples"].append(state)
    with open('examples.json','w') as f:
        json.dump(config, f)
    lock.release()




def multiplierToNumber(ml):
    if ml == None:
        return 0
    if ml == "DL":
        return 1
    if ml == "TL":
        return 2
    if ml == "DW":
        return 3
    if ml == "TW":
        return 4

def mapBoardToState(game, leave):
    state = {}
    bag = [0] * 27
    rack = [0] * 27
    for letter in game.bag:
        if letter == '?':
            bag[0] += 1
        else:
            bag[ord(letter) - 64] += 1
    for letter in game.players[game.currentPlayer].rack:
        if letter == '?':
            bag[0] += 1
        else:
            bag[ord(letter) - 64] += 1
    state['bag'] = bag
    for letter in leave:
        if letter == '?':
            rack[0] += 1
        else:
            rack[ord(letter) - 64] += 1
    state['rack'] = rack
    state['score'] = [game.players[not game.currentPlayer].score, game.players[not game.currentPlayer].score - game.players[game.currentPlayer].score]
    board = [[[0,0] for i in range(15)] for j in range(15)]
    for i in range(len(game.board.board)):
        for j in range(len(game.board.board)):
            board[i][j][0] = 0 if game.board.board[i][j].letter == None else ord(game.board.board[i][j].letter.upper()) - 64
            board[i][j][1] = multiplierToNumber(game.board.board[i][j].multiplier)
    state['board'] = board
    return state




def thread_func(move, game, ply, lock):
    lettersUsed = game.board.get_letters_used(move[2], move[0], move[3])
    lettersLeft = game.players[game.currentPlayer].rack[:]
    for letter in game.players[game.currentPlayer].rack:
        if letter.islower() and "?" in game.players[game.currentPlayer].rack:
            lettersLeft.remove("?")
        elif letter in lettersUsed:
            lettersLeft.remove(letter)
    print(lettersLeft, move[0])
    for _ in range(10):
        temp_board = copy.deepcopy(game.board)
        temp_players = copy.deepcopy(game.players)
        temp_game = copy.copy(game)
        temp_game.players = temp_players
        temp_game.board = temp_board
        temp_game.exchangeSeven(not temp_game.currentPlayer)
        temp_game.players[temp_game.currentPlayer].score += move[1]
        temp_game.play(move[2], move[0], move[3])
        state = mapBoardToState(temp_game, lettersLeft, lock)
        temp_game.playBestMove()
        for __ in range(ply - 1):
            temp_game.playBestMove()
            temp_game.playBestMove()
        diff = temp_game.players[temp_game.currentPlayer].score - temp_game.players[not temp_game.currentPlayer].score
        state['scoreDifferentialAfterXPly'] = diff
        saveExample(state)
    print(move[0])


def simulate(game, ply=2):
    lock = threading.Lock()
    print('hi')
    moves = game.find_best_moves(game.players[game.currentPlayer].rack, 5)
    threads = []
    for move in moves:
        threads.append(threading.Thread(target=thread_func, args=(move, game, ply, lock,)))
    for th in threads:
        th.start()
    for th in threads:
        th.join()


def main():
    a = Game()
    while a.numMoves >= 0:
        simulate(a)
        a.playBestMove()
        if a.numMoves % 5 == 0:
            print(a.board)


if __name__ == "__main__":
    main()


