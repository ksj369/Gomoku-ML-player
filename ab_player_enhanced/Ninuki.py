#!/usr/bin/python3
# Set the path to your python3 above

"""
Go0 random Go player
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


def heuristic_eval(board):
        """
        Returns: a very basic heuristic value of the board
        Currently only considers captures
        """
        if board.current_player == BLACK:
            return (board.black_captures - board.white_captures) / 10
        else:
            return (board.white_captures - board.black_captures) / 10

def heuristic_eval_move(board, move):
        """
        Slightly more robust heuristic, needs more fine-tuning
        """
        total_score = 0

        if board.current_player == BLACK:
            total_score += (board.black_captures - board.white_captures) / 10
        else:
            total_score += (board.white_captures - board.black_captures) / 10
        
        row_count = board.count_stones_in_row(move, board.current_player)
        total_score += row_count / 5

        
        if move in [board.moves_for_n_in_a_row(board.current_player, GoBoardUtil.get_twoD_board(board), 5)]:
            total_score += 100
        if move in [board.moves_for_n_in_a_row(board.current_player, GoBoardUtil.get_twoD_board(board), 4)]:
            total_score += 10
        if move in [board.moves_for_n_in_a_row(board.current_player, GoBoardUtil.get_twoD_board(board), 3)]:
            total_score += 0.5
        

        return total_score

class ABPlayer(GoEngine):
    def __init__(self) -> None:
        """
        Ninuki player which uses basic iterative deepening alpha-beta search.
        Many improvements are possible.
        """
        GoEngine.__init__(self, "Go0", 1.0)
        self.time_limit = 1

    def get_move(self, board: GoBoard, color: GO_COLOR) -> GO_POINT:
        if board.get_empty_points().size == 0:
            return "pass"
        if color == 'w':
            board.current_player = WHITE
        else:
            board.current_player = BLACK
        winner, move = self.solve_board(board)
        return format_point(point_to_coord(self.best_move, self.board.size)).lower()

    def alpha_beta(self, alpha, beta, depth):
        if time.time() - self.solve_start_time > (self.time_limit - 0.01):
            return 0, False, True

        is_terminal, winner = self.board.is_terminal()
        if is_terminal:
            if winner == self.board.current_player:
                return float('inf'), True, False
            elif winner == opponent(self.board.current_player):
                return float('-inf'), True, False
            else:
                return 0, True, False

        if depth >= self.max_depth:
            state = self.board.copy()
            return heuristic_eval(state), False, False  # Evaluate the position using your heuristic

        any_unsolved = False
        moves = []
        # Check for moves that result in a five-in-a-row
        priority_moves = self.board.moves_for_n_in_a_row(self.board.current_player, GoBoardUtil.get_twoD_board(self.board), 4)
        if priority_moves:
            moves = priority_moves
        else:
            # If no priority moves, use the standard legal moves
            moves = GoBoardUtil.generate_legal_moves(self.board, self.board.current_player)
        if depth == 0:
            random.shuffle(moves)


        for move in moves:
            self.board.play_move(move, self.board.current_player)
            
            value, solved, timeout = self.alpha_beta(-beta, -alpha, depth+1)
            # The following evaluation function is commented out because it was not performing as expected
            #TODO: Improve heuristic_eval_move function
            # value = heuristic_eval_move(self.board, move)
            self.board.undo()
            value = -value

            if timeout:
                return 0, False, True
            
            if not solved:
                any_unsolved = True

            if value > alpha:
                alpha = value
                if depth == 0:
                    self.best_move = move

            if solved and value == float('inf'):
                return float('inf'), True, False

            if value >= beta:
                return beta, True, False
        
        return alpha, not any_unsolved, False


    def solve_board(self, board):
        self.solve_start_time = time.time()
        self.board = board.copy()
        self.tt = {}
        if self.board.get_empty_points().size == 0:
            self.best_move = PASS
        else:
            self.best_move = self.board.get_empty_points()[0]

        solved = False
        timeout = False
        self.max_depth = 1
        while not solved and not timeout:
            result, solved, timeout = self.alpha_beta(-1, 1, 0)
            self.max_depth += 1
        
        if timeout:
            return "unknown", None
        elif result == 1:
            if self.board.current_player == BLACK:
                return "b", format_point(point_to_coord(self.best_move, self.board.size)).lower()
            else:
                return "w", format_point(point_to_coord(self.best_move, self.board.size)).lower()
        elif result == -1:
            if self.board.current_player == BLACK:
                return "w", None
            else:
                return "b", None
        else:
            return "draw", format_point(point_to_coord(self.best_move, self.board.size)).lower()

    def set_time_limit(self, time_limit):
        self.time_limit = time_limit

def run() -> None:
    """
    start the gtp connection and wait for commands.
    """
    board: GoBoard = GoBoard(DEFAULT_SIZE)
    con: GtpConnection = GtpConnection(ABPlayer(), board)
    con.start_connection()


if __name__ == "__main__":
    run()
