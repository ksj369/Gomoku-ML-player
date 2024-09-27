"""
board.py
Cmput 455 sample code
Written by Cmput 455 TA and Martin Mueller

Implements a basic Go board with functions to:
- initialize to a given board size
- check if a move is legal
- play a move

The board uses a 1-dimensional representation with padding
"""

import numpy as np
from typing import List, Tuple

from board_base import (
    board_array_size,
    coord_to_point,
    is_black_white,
    is_black_white_empty,
    opponent,
    where1d,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    MAXSIZE,
    NO_POINT,
    PASS,
    GO_COLOR,
    GO_POINT,
)


"""
The GoBoard class implements a board and basic functions to play
moves, check the end of the game, and count the acore at the end.
The class also contains basic utility functions for writing a Go player.
For many more utility functions, see the GoBoardUtil class in board_util.py.

The board is stored as a one-dimensional array of GO_POINT in self.board.
See coord_to_point for explanations of the array encoding.
"""
class GoBoard(object):
    def __init__(self, size: int) -> None:
        """
        Creates a Go board of given size
        """
        assert 2 <= size <= MAXSIZE
        self.reset(size)
        self.black_captures = 0
        self.white_captures = 0
        self.depth = 0
        self.black_capture_history = []
        self.white_capture_history = []
        self.move_history = []

    def add_two_captures(self, color: GO_COLOR) -> None:
        if color == BLACK:
            self.black_captures += 2
        elif color == WHITE:
            self.white_captures += 2
    
    def get_captures(self, color: GO_COLOR) -> None:
        if color == BLACK:
            return self.black_captures
        elif color == WHITE:
            return self.white_captures
    
    def reset(self, size: int) -> None:
        """
        Creates a start state, an empty board with given size.
        """
        self.size: int = size
        self.NS: int = size + 1
        self.WE: int = 1
        self.last_move: GO_POINT = NO_POINT
        self.last2_move: GO_POINT = NO_POINT
        self.current_player: GO_COLOR = BLACK
        self.maxpoint: int = board_array_size(size)
        self.board: np.ndarray[GO_POINT] = np.full(self.maxpoint, BORDER, dtype=GO_POINT)
        self._initialize_empty_points(self.board)
        self.black_captures = 0
        self.white_captures = 0
        self.depth = 0
        self.black_capture_history = []
        self.white_capture_history = []
        self.move_history = []

    def copy(self) -> 'GoBoard':
        b = GoBoard(self.size)
        assert b.NS == self.NS
        assert b.WE == self.WE
        b.last_move = self.last_move
        b.last2_move = self.last2_move
        b.current_player = self.current_player
        assert b.maxpoint == self.maxpoint
        b.board = np.copy(self.board)
        b.black_captures = self.black_captures
        b.white_captures = self.white_captures
        b.depth = self.depth
        b.black_capture_history = self.black_capture_history.copy()
        b.white_capture_history = self.white_capture_history.copy()
        b.move_history = self.move_history.copy()
        return b

    def get_color(self, point: GO_POINT) -> GO_COLOR:
        return self.board[point]

    def pt(self, row: int, col: int) -> GO_POINT:
        return coord_to_point(row, col, self.size)

    def is_legal(self, point: GO_POINT, color: GO_COLOR) -> bool:
        """
        Check whether it is legal for color to play on point
        This method tries to play the move on a temporary copy of the board.
        This prevents the board from being modified by the move
        """
        if point == PASS:
            return True
        #board_copy: GoBoard = self.copy()
        #can_play_move = board_copy.play_move(point, color)
        #return can_play_move
        return self.board[point] == EMPTY

    def end_of_game(self) -> bool:
        return self.get_empty_points().size == 0 or (self.last_move == PASS and self.last2_move == PASS)
           
    def get_empty_points(self) -> np.ndarray:
        """
        Return:
            The empty points on the board
        """
        return where1d(self.board == EMPTY)

    def row_start(self, row: int) -> int:
        assert row >= 1
        assert row <= self.size
        return row * self.NS + 1

    def _initialize_empty_points(self, board_array: np.ndarray) -> None:
        """
        Fills points on the board with EMPTY
        Argument
        ---------
        board: numpy array, filled with BORDER
        """
        for row in range(1, self.size + 1):
            start: int = self.row_start(row)
            board_array[start : start + self.size] = EMPTY

    def play_move(self, point: GO_POINT, color: GO_COLOR) -> bool:
        """
        Tries to play a move of color on the point.
        Returns whether or not the point was empty.
        """
        if self.board[point] != EMPTY:
            return False
        self.board[point] = color
        self.current_player = opponent(color)
        self.last2_move = self.last_move
        self.last_move = point
        O = opponent(color)
        offsets = [1, -1, self.NS, -self.NS, self.NS+1, -(self.NS+1), self.NS-1, -self.NS+1]
        bcs = []
        wcs = []
        for offset in offsets:
            if self.board[point+offset] == O and self.board[point+(offset*2)] == O and self.board[point+(offset*3)] == color:
                self.board[point+offset] = EMPTY
                self.board[point+(offset*2)] = EMPTY
                if color == BLACK:
                    self.black_captures += 2
                    bcs.append(point+offset)
                    bcs.append(point+(offset*2))
                else:
                    self.white_captures += 2
                    wcs.append(point+offset)
                    wcs.append(point+(offset*2))
        self.depth += 1
        self.black_capture_history.append(bcs)
        self.white_capture_history.append(wcs)
        self.move_history.append(point)
        return True
    
    def undo(self):
        self.board[self.move_history.pop()] = EMPTY
        self.current_player = opponent(self.current_player)
        self.depth -= 1
        bcs = self.black_capture_history.pop()
        for point in bcs:
            self.board[point] = WHITE
            self.black_captures -= 1
        wcs = self.white_capture_history.pop()
        for point in wcs:
            self.board[point] = BLACK
            self.white_captures -= 1
        if len(self.move_history) > 0:
            self.last_move = self.move_history[-1]
        if len(self.move_history) > 1:
            self.last2_move = self.move_history[-2]

    def neighbors_of_color(self, point: GO_POINT, color: GO_COLOR) -> List:
        """ List of neighbors of point of given color """
        nbc: List[GO_POINT] = []
        for nb in self._neighbors(point):
            if self.get_color(nb) == color:
                nbc.append(nb)
        return nbc

    def _neighbors(self, point: GO_POINT) -> List:
        """ List of all four neighbors of the point """
        return [point - 1, point + 1, point - self.NS, point + self.NS]

    def _diag_neighbors(self, point: GO_POINT) -> List:
        """ List of all four diagonal neighbors of point """
        return [point - self.NS - 1,
                point - self.NS + 1,
                point + self.NS - 1,
                point + self.NS + 1]

    def last_board_moves(self) -> List:
        """
        Get the list of last_move and second last move.
        Only include moves on the board (not NO_POINT, not PASS).
        """
        board_moves: List[GO_POINT] = []
        if self.last_move != NO_POINT and self.last_move != PASS:
            board_moves.append(self.last_move)
        if self.last2_move != NO_POINT and self.last2_move != PASS:
            board_moves.append(self.last2_move)
        return board_moves

    def full_board_detect_five_in_a_row(self) -> GO_COLOR:
        """
        Returns BLACK or WHITE if any five in a row is detected for the color
        EMPTY otherwise.
        Checks the entire board.
        """
        for point in range(self.maxpoint):
            c = self.board[point]
            if c != BLACK and c != WHITE:
                continue
            for offset in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                i = 1
                num_found = 1
                while self.board[point + i * offset[0] * self.NS + i * offset[1]] == c:
                    i += 1
                    num_found += 1
                i = -1
                while self.board[point + i * offset[0] * self.NS + i * offset[1]] == c:
                    i -= 1
                    num_found += 1
                if num_found >= 5:
                    return c
        
        return EMPTY
    
    def detect_five_in_a_row(self) -> GO_COLOR:
        """
        Returns BLACK or WHITE if any five in a row is detected for the color
        EMPTY otherwise.
        Only checks around the last move for efficiency.
        """
        if self.last_move == NO_POINT or self.last_move == PASS:
            return EMPTY
        c = self.board[self.last_move]
        for offset in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            i = 1
            num_found = 1
            while self.board[self.last_move + i * offset[0] * self.NS + i * offset[1]] == c:
                i += 1
                num_found += 1
            i = -1
            while self.board[self.last_move + i * offset[0] * self.NS + i * offset[1]] == c:
                i -= 1
                num_found += 1
            if num_found >= 5:
                return c
        
        return EMPTY

    def is_terminal(self):
        """
        Returns: is_terminal, winner
        If the result is a draw, winner = EMPTY
        """
        winner = self.detect_five_in_a_row()
        if winner != EMPTY:
            return True, winner
        elif self.get_captures(BLACK) >= 10:
            return True, BLACK
        elif self.get_captures(WHITE) >= 10:
            return True, WHITE
        elif self.end_of_game():
            return True, EMPTY
        else:
            return False, EMPTY

    def heuristic_eval(self):
        """
        Returns: a very basic heuristic value of the board
        Currently only considers captures
        """
        if self.current_player == BLACK:
            return (self.black_captures - self.white_captures) / 10
        else:
            return (self.white_captures - self.black_captures) / 10

    def state_to_str(self):
        state = np.array2string(self.board, separator='')
        state += str(self.current_player)
        state += str(self.black_captures)
        state += str(self.white_captures)
        return state
    
    def detect_open_fours(self, point: GO_POINT, color: GO_COLOR) -> bool:
        """
        Check if there is an open four of the given color around the specified point.
        """
        for offset in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            if self._check_open_four_in_direction(point, offset, color):
                return True
        return False

    def _check_open_four_in_direction(self, point: GO_POINT, offset: Tuple[int, int], color: GO_COLOR) -> bool:
        """
        Helper function to check for an open four in a specific direction.
        """
        c = self.board[point]
        num_found = 1
        empty_found = 0

        # Check in the positive direction
        i = 1
        while self.board[point + i * offset[0] * self.NS + i * offset[1]] == c:
            i += 1
            num_found += 1

        # Check for an open end
        if self.board[point + i * offset[0] * self.NS + i * offset[1]] == EMPTY:
            empty_found += 1

        # Check in the negative direction
        i = -1
        while self.board[point + i * offset[0] * self.NS + i * offset[1]] == c:
            i -= 1
            num_found += 1

        # Check for an open end
        if self.board[point + i * offset[0] * self.NS + i * offset[1]] == EMPTY:
            empty_found += 1

        # Check if it's an open four
        return num_found == 4 and empty_found == 2
    
    def count_stones_in_row(self, point: GO_POINT, color: GO_COLOR) -> int:
        """
        Count the number of stones in a row for the given color around the specified point.
        """
        count = 1  # Count the stone at the specified point
        c = self.board[point]

        # Check in the positive direction
        i = 1
        while self.board[point + i] == c:
            i += 1
            count += 1

        # Check in the negative direction
        i = -1
        while self.board[point + i] == c:
            i -= 1
            count += 1

        return count

    def detect_open_threes(self, point: GO_POINT, color: GO_COLOR) -> bool:
        """
        Check if there is an open three of the given color around the specified point.
        """
        for offset in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            if self._check_open_three_in_direction(point, offset, color):
                return True
        return False

    def _check_open_three_in_direction(self, point: GO_POINT, offset: Tuple[int, int], color: GO_COLOR) -> bool:
        """
        Helper function to check for an open three in a specific direction.
        """
        c = self.board[point]
        num_found = 1
        empty_found = 0

        # Check in the positive direction
        i = 1
        while self.board[point + i * offset[0] * self.NS + i * offset[1]] == c:
            i += 1
            num_found += 1

        # Check for an open end
        if self.board[point + i * offset[0] * self.NS + i * offset[1]] == EMPTY:
            empty_found += 1

        # Check in the negative direction
        i = -1
        while self.board[point + i * offset[0] * self.NS + i * offset[1]] == c:
            i -= 1
            num_found += 1

        # Check for an open end
        if self.board[point + i * offset[0] * self.NS + i * offset[1]] == EMPTY:
            empty_found += 1

        # Check if it's an open three
        return num_found == 3 and empty_found == 2

    def moves_for_n_in_a_row(self, player_color: GO_COLOR, twoD_board, n) -> List[GO_POINT]:
        winning_moves = []

        if self.last_move == NO_POINT or self.last_move == PASS:
            return EMPTY

        c = self.board[self.last_move]
        if c != player_color:
            return EMPTY

        size = self.size

        for offset in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            i = np.arange(1, 6)
            points_forward = (
                np.array([self.last_move])[:, None]
                + i * offset[0] * size
                + i * offset[1]
            )
            points_backward = (
                np.array([self.last_move])[:, None]
                - i * offset[0] * size
                - i * offset[1]
            )

            forward_values = twoD_board[points_forward // size % size, points_forward % size]
            backward_values = twoD_board[points_backward // size % size, points_backward % size]

            forward_mask = forward_values == c
            backward_mask = backward_values == c

            forward_counts = np.cumsum(forward_mask, axis=0)
            backward_counts = np.cumsum(backward_mask, axis=0)

            forward_counts[~forward_mask] = 0
            backward_counts[~backward_mask] = 0

            num_found_forward = np.max(forward_counts, axis=0)
            num_found_backward = np.max(backward_counts, axis=0)

            num_found = num_found_forward + num_found_backward + 1

            # Include both 4 and 5 in a row situations
            winning_moves.extend(points_forward[np.where(num_found >= n)[0]].flatten())
            winning_moves.extend(points_backward[np.where(num_found >= n)[0]].flatten())

            # Check for capturing moves
            capturing_moves = []
            for i in range(1, 6):
                neighbor_offsets = np.array([-1, 0, 1])
                neighbor_points_x = (
                    np.array([self.last_move])[:, None]
                    + i * offset[0] * neighbor_offsets
                )
                neighbor_points_y = (
                    np.array([self.last_move])[:, None]
                    + i * offset[1] * neighbor_offsets
                )

                neighbor_points = neighbor_points_x * size + neighbor_points_y

                opponent_stones = twoD_board[neighbor_points // size, neighbor_points % size] == opponent(player_color)
                captures_per_point = np.sum(opponent_stones, axis=2)

                capturing_moves.extend(
                    neighbor_points.flatten()[captures_per_point >= 1].tolist()
                )

        return list(set(winning_moves + capturing_moves))