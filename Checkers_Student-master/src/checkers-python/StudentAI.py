from random import choice, randint
from BoardClasses import Board
from collections import defaultdict
import math
import copy
import time

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.


class TreeNode(object):

    def __init__(self, parent, move = None):
        self._move = move
        self._parent = parent
        self._children = dict()
        self._rewards = 0
        self._visits = 0
        self._UCT = 0

    def expand(self, board, player):
        possible_moves = board.get_all_possible_moves(player)
        for moves in possible_moves:
            for move in moves:
                if move not in self._children:
                    self._children[move] = TreeNode(self, move)

    def traverse(self):
        unvisited = []
        fully_expanded = True
        if len(self._children) == 0:
            return self
        for c in self._children.values():
            if c._visits == 0:
                fully_expanded = False
                unvisited.append(c)
        if fully_expanded:
            return self.best_UCT(self)
        return choice(unvisited)

    def best_UCT(self, node):
        for c in node._children.values():
            c._UCT = (c._rewards / c._visits) + math.sqrt(2) * (math.sqrt(math.log2(c._parent._visits) / c._visits))
        return max(node._children.items(), key=lambda child:child[1]._UCT)[1]


class MCTS(object):

    def __init__(self):
        self._root = TreeNode(None)
        self._playouts = 800

    def get_move(self, board, player):
        self._root = TreeNode(None)
        possible_moves = board.get_all_possible_moves(player)
        move = []
        for moves in possible_moves:
            move.extend(moves)
        if len(move) == 1:
            return move[0]
        else:
            self._root.expand(board, player)
            i = 0
            while i < self._playouts:
                leaf = self._root.traverse()
                c_board = copy.deepcopy(board)
                c_board.make_move(leaf._move, player)
                sim_result = self.play(c_board, player, 800)
                self.backpropagate(leaf, sim_result)
                i += 1
            return self.best_move(self._root)

    def play(self, board, player, limit):
        c_player = player
        c_board = copy.deepcopy(board)
        i = 0
        while i in range(limit):
            winner = c_board.is_win(c_player)
            if winner != 0:
                break
            if c_player == 1:
                c_player = 2
            else:
                c_player = 1
            possible_moves = []
            all_moves = c_board.get_all_possible_moves(c_player)
            for moves in all_moves:
                possible_moves.extend(moves)
            if len(possible_moves) == 0:
                break
            c_board.make_move(choice(possible_moves),c_player)
        if winner == 0:
            return 0
        if winner == player:
            return 1
        return -1

    def backpropagate(self, node, result):
        if node._parent == None:
            node._rewards += result
            node._visits += 1
            return
        node._rewards += result
        node._visits += 1
        self.backpropagate(node._parent, result)

    def best_move(self, node):
        return max(node._children.items(), key=lambda child:child[1]._visits)[0]

    def update_root(self, move):
        self._root = self._root._children[move]
        self._root._parent = None


class StudentAI:

    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.opponent = {1: 2, 2: 1}
        self.color = 2

        self.MCTS = MCTS()

        self.max_timer = 480
        self.time_left = self.max_timer
        self.quick = False
        self.shorten = False

    def get_move(self, move):
        start_time = time.time()
        if self.time_left <= 120 and not self.shorten:
            self.shorten = True
            self.MCTS._playouts = self.MCTS._playouts * 0.85
        if self.time_left <= 30 and not self.quick:
                self.quick = True
        # if self.time_left <= 0:
        #         print("It's been 8 minutes")
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
        if self.quick:
            move = self.quick_move(move)
            self.board.make_move(move, self.color)
            self.time_left -= time.time() - start_time
            return move
        move = self.MCTS.get_move(self.board, self.color)
        self.board.make_move(move, self.color)
        self.time_left -= time.time() - start_time
        return move

    def quick_move(self, move):
        opp_color = self.opponent[self.color]
        possible_moves = self.board.get_all_possible_moves(self.color)
        best_move = move
        best_move_dist = 2
        capture = False
        for moves in possible_moves:
            for move in moves:
                if len(move) >= best_move_dist:
                    if len(move) > best_move_dist:
                        best_move_dist = len(move)
                        best_move = move
                        capture = True
                elif best_move_dist == 2:
                    start = move[0]
                    end = move[0]
                    if abs(start[0] - end[0]) + abs(start[1] - end[1]) > 2:
                        best_move = move
                        capture = True
        if not capture:
            best_moves = find_best_moves(self.board, self.color, opp_color)
            rand_index = randint(0, len(best_moves) - 1)
            best_move = best_moves[rand_index]
        return best_move


def count_captures(board, player_two):
    count = 0
    possible_moves = board.get_all_possible_moves(player_two)
    for moves in possible_moves:
        for move in moves:
            start = move[0]
            end = move[1]
            most_movement = max(abs(start[0] - end[0]), abs(start[1] - end[1]))
            if most_movement > 1:
                count += most_movement
    return count


def find_best_moves(board, player_one, player_two):
    captures = defaultdict(list)
    result = []
    possible_moves = board.get_all_possible_moves(player_one)
    for moves in possible_moves:
        for move in moves:
            current_boardstate = copy.deepcopy(board)
            current_boardstate.make_move(move, player_one)
            eval = count_captures(current_boardstate, player_two)
            if eval > 0:
                captures[eval].append(move)
            else:
                result.append(move)
    if not result:
        return captures[sorted(captures.keys())[0]]
    return result