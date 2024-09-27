#!/usr/bin/python3
# Set the path to your python3 above

"""
Cmput 455 sample code
Written by Cmput 455 TA and Martin Mueller
"""
from gtp_connection import GtpConnection, format_point, point_to_coord
from board_base import DEFAULT_SIZE, GO_POINT, GO_COLOR
from board import GoBoard
from board_util import GoBoardUtil
from engine import GoEngine
import time
import random
from board_base import (
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    GO_COLOR, GO_POINT,
    PASS,
    MAXSIZE,
    coord_to_point,
    opponent
)
import math

class Node:
    def __init__(self, board, move=None, parent=None):
        self.board = board
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0

    def UCTSelectChild(self):
        # Select a child node based on UCT (Upper Confidence Bound for Trees) formula
        log_total_visits = math.log(self.visits)
        child = max(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * log_total_visits / c.visits))
        return child

    def AddChild(self, move, state):
        # Add a child node for a given move and state
        child = Node(board=state.copy(), move=move, parent=self)
        self.children.append(child)
        return child

    def Update(self, result):
        # Update the node's statistics with the result of a simulation
        self.visits += 1
        self.wins += result

    def TreeToString(self, indent):
        # Output the tree structure as a string (for debugging)
        s = self.IndentString(indent) + str(self)
        for child in self.children:
            s += child.TreeToString(indent + 1)
        return s

    def ChildrenToString(self):
        # Output the children as a string (for debugging)
        s = ""
        for child in self.children:
            s += str(child) + "\n"
        return s

    def IndentString(self, indent):
        # Helper method for indentation
        s = "\n"
        for _ in range(indent):
            s += "| "
        return s

def ninuki_heuristic(board, move, color):
    # Copy the board to simulate the move
    temp_board = board.copy()
    temp_board.play_move(move, color)

    # Check if the move results in an immediate win
    if temp_board.full_board_detect_five_in_a_row() == color:
        return float('inf')  # Immediate win is highly rewarded

    # Check if the move blocks the opponent's potential win
    if temp_board.full_board_detect_five_in_a_row() == opponent:
        return float('-inf')  # Blocking opponent's win is crucial

    # Check if the move contributes to capturing stones
    captured_stones = temp_board.get_captures(color)
    capture_reward = captured_stones  # Gradual positive reinforcement

    # Check for open-four patterns
    if temp_board.detect_open_fours(move, color):
        return float('5.0')  # Open four is a powerful winning move

    # Check for open-three patterns
    if temp_board.detect_open_threes(move, color):
        return 0.8  # Open three is a good move, but not as powerful as open four

    # # Check for potential double-threat moves
    # if temp_board.detect_double_threats(move, color):
    #     return 0.5  # Double-threat moves can lead to advantageous positions

    # Evaluate the move based on the number of stones in a row and captured stones
    row_count = temp_board.count_stones_in_row(move, color)

    # Prioritize moves with more stones in a row and more captured stones
    return row_count + capture_reward



class MCTSPlayer(GoEngine):
    def __init__(self) -> None:
        GoEngine.__init__(self, "MCTSPlayer", 1.0)
        self.time_limit = 1
        self.initial_simulations = 1000  # Initial number of simulations
        self.ucb_constant = 1.1

    def get_move(self, board: GoBoard, color: GO_COLOR) -> GO_POINT:
        root = Node(board.copy())
        start_time = time.time()
        remaining_time = self.time_limit

        while time.time() - start_time < remaining_time:
            node = root
            state = board.copy()

            # Select
            while node.children != []:  # node is fully expanded and non-terminal
                node = node.UCTSelectChild()
                state.play_move(node.move, state.current_player)

            # Expand
            if not state.is_terminal()[0]:  # if the state is non-terminal
                legal_moves = GoBoardUtil.generate_legal_moves(state, state.current_player)
                
                #Calculate move values
                move_values = [(child.wins / child.visits) if child.visits > 0 else 0 for child in node.children]
                
                if move_values:
                    # Choose the move with the maximum value
                    m = legal_moves[move_values.index(max(move_values))]
                else:
                    # If move_values is empty, choose a random move
                    m = random.choice(legal_moves)
                
                state.play_move(m, state.current_player)
                node = node.AddChild(m, state)  # add child and descend tree

            # Rollout
            while not state.is_terminal()[0]:  # while state is non-terminal
                legal_moves = GoBoardUtil.generate_legal_moves(state, state.current_player)
                if not legal_moves:
                    break  # No legal moves left

                values = [self.heuristic(state, move, state.current_player) for move in legal_moves]
                best_move = legal_moves[values.index(max(values))]

                
                if best_move not in legal_moves:
                    # If the chosen move is not legal, choose a random legal move
                    best_move = random.choice(legal_moves)

                state.play_move(best_move, state.current_player)

            # Backpropagate
            result = state.is_terminal()[1]
            while node is not None:  # backpropagate from the expanded node and work back to the root node
                node.Update(result)
                node = node.parent

            # Adjust the number of simulations dynamically
            remaining_time = self.time_limit - (time.time() - start_time)
            if remaining_time > 0:
                self.adjust_simulations(remaining_time)

        # Return the move that was most visited
        return sorted(root.children, key=lambda c: c.visits)[-1].move

    def adjust_simulations(self, remaining_time):
        # Adjust the number of simulations based on remaining time
        if remaining_time > 0.5 * self.time_limit and self.initial_simulations > 500:
            self.initial_simulations //= 2
        elif remaining_time < 0.2 * self.time_limit and self.initial_simulations < 5000:
            self.initial_simulations *= 2

    def set_time_limit(self, time_limit):
        self.time_limit = time_limit


    def heuristic(self, board, move, color):
        return ninuki_heuristic(board, move, color)



def run() -> None:
    board: GoBoard = GoBoard(MAXSIZE)
    con: GtpConnection = GtpConnection(MCTSPlayer(), board)
    con.start_connection()

if __name__ == "__main__":
    run()
