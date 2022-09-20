import copy
import math
import random

from BoardClasses import Move
from BoardClasses import Board


# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

class MCTSNode(object):

    def __init__(self, parent, move=None):
        self.move = move
        self.parent = parent
        self.children = []
        self.win = 3
        self.samples = 3
        self.uct = 0


def best_uct(node):
    best_value = 0
    best_child = None

    for child in node.children:
        child.uct = (child.win / child.samples) + 2 * (math.sqrt(math.log(child.parent.samples, 10) / child.samples))
        if child.uct > best_value:
            best_value = child.uct
            best_child = child
        elif child.uct == best_value:
            random_pick = [best_child, child]
            best_child = random.choice(random_pick)

    return best_child



class StudentAI():

    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1: 2, 2: 1}
        self.color = 2
        self.root = MCTSNode(None)

    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        best = self.mcts()

        self.board.make_move(best.move, self.color)
        return best.move

    def traverse(self, node):
        unvisited_children = []
        not_leaf = True

        for child in node.children:
            if child.samples == 0:
                not_leaf = False
                unvisited_children.append(child)
        #go to next best uct node
        if not_leaf:
            return best_uct(node)
        return random.choice(unvisited_children)



    def mcts(self):
        self.root = MCTSNode(None)
        
        next_moves = self.board.get_all_possible_moves(self.color)
        flat_list = [item for sublist in next_moves for item in sublist]
        for moves in flat_list:
            self.root.children.append(MCTSNode(self.root, moves))
            
        for i in range(600):
            leaf = None
            if len(self.root.children) != 0:
                leaf = self.traverse(self.root)
            else:
                leaf = self.root
            if leaf != None:
                simulation = self.rollout(leaf)
                self.backprop(leaf, simulation)

        return self.best_child()

    def best_child(self):

        best_value = 0
        best_child = None

        for child in self.root.children:
            if child.samples > best_value:
                best_value = child.samples
                best_child = child
            elif child.uct == best_value:
                random_pick = [best_child, child]
                best_child = random.choice(random_pick)

        return best_child

    def backprop(self, leaf, simulation):
        if leaf == None:
            return
        leaf.samples = leaf.samples + 1
        leaf.win = leaf.win + simulation
        self.backprop(leaf.parent, simulation)

    def rollout(self, leaf):
        board = copy.deepcopy(self.board)
        board.make_move(leaf.move, self.color)

        turn = self.color

        winRes = board.is_win(self.color)
        # not terminate
        while winRes == 0:

            if turn == 2:
                turn = 1
            else:
                turn = 2
                
            next_moves = board.get_all_possible_moves(turn)
            if len(next_moves) == 0:
                break
            flat_list = [item for sublist in next_moves for item in sublist]
        
            board.make_move(random.choice(flat_list), turn)
          

            winRes = board.is_win(turn)


        # how to count tie??
        if winRes == 0:
            return 0
        # win
        if winRes == self.color:
            return 1
        # lose
        
        return 0