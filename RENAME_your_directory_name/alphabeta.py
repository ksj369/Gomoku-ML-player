
from board_util import GoBoardUtil
from board import EMPTY
from board_base import opponent

def terminal(board):
    #check terminal state of game and assign win/loss in branch
    is_terminal,winner=board.is_terminal()
    if is_terminal:
        if winner==board.current_player():
            return 1
        else:
            return -1
      # for draw to prevent only win/losse situation  
    if len(board.empty_moves())==0:
        return 0
    return None


def alphabeta(board,alpha,beta):

    end=terminal(board)
    if end!=None:
        return end
    # check simulated moves first then go on anylegal moves

    # simulations=board.monte_carlo_list()
    # if simulations:
    #     board.play_move(simulations[0],board.current_player)
    #     end=-alphabeta(board,-beta,-alpha)
    #     if end>alpha:
    #         alpha=end
    #     board.board[simulations[0]]=EMPTY
    #     board.current_player=opponent(board.current_player)
    #     if end>=beta:
    #         return beta
        
    # else:


    # legal block to be intended after simutaions implementations

    for moves in GoBoardUtil.generate_legal_moves(board):
        board.play_move(moves,board.current_player)
        end=-alphabeta(board,-beta,-alpha)
        if end>alpha:
            alpha=end
        board.board[moves]=EMPTY
        board.current_player=opponent(board.current_player)
        if end>=beta:
            return beta
        
    
        return alpha





   
    
        