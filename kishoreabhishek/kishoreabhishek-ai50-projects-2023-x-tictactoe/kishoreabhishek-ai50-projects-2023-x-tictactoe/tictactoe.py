"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    xcnt=0
    ocnt=0
    for i in range(3):
        xcnt = xcnt + board[i].count('X')
        ocnt = ocnt + board[i].count('O')
    if xcnt==0 and ocnt==0:
        return 'X'
    elif xcnt>ocnt:
        return 'O'
    else:
        return 'X'




def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    availableactions=set()
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                availableactions.add((i,j))
    return availableactions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    newboard = [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]
    for i in range(3):
        for j in range(3):
            newboard[i][j] = board[i][j]

    newboard[action[0]][action[1]] = player(board)
    return newboard

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    winner=None
    xcnt=[0,0,0]
    ocnt=[0,0,0]
    diagxcnt1=0
    diagxcnt2 =0
    diagocnt1=0
    diagocnt2=0
    for i in range(3):
        if board[i].count('X') == 3:
            winner='X'
            break
        elif board[i].count('O') == 3:
            winner='O'
            break
    for i in range(3):
        if board[i][0] == 'X':
            xcnt[0] = xcnt[0]+1
        if board[i][0] == 'O':
            ocnt[0] = ocnt[0]+1
        if board[i][1] == 'X':
            xcnt[1] = xcnt[1]+1
        if board[i][1] == 'O':
            ocnt[1] = ocnt[1]+1
        if board[i][2] == 'X':
            xcnt[2] = xcnt[2]+1
        if board[i][2] == 'O':
            ocnt[2] = ocnt[2]+1
        if board[i][i] == 'X':
            diagxcnt1 = diagxcnt1+1
        if board[i][i] == 'O':
            diagocnt1 = diagocnt1+1
        if board[i][2-i] == 'X':
            diagxcnt2 = diagxcnt2+1

        if board[i][2-i] == 'O':
            diagocnt2 = diagocnt2+1
    if 3 in xcnt or diagxcnt1==3 or diagxcnt2==3:
        winner='X'
    elif 3 in ocnt or diagocnt1==3 or diagocnt2==3:
        winner='O'
    return winner


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == 'X' or winner(board) == 'O':
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                return False

    return True



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    u=0
    if terminal(board):
        if winner(board) == 'X':
            u=1
        elif winner(board) == 'O':
            u=-1
    return u

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    p = player(board)
    opaction=None
    if p=='X':
        v = float('-inf')
    else:
        v=float('inf')
    for action in actions(board):
        if p=='X':
            if max(v,minValue(result(board,action)))>v:
                v = minValue(result(board,action))
                opaction = action
        else:
            if min(v,maxValue(result(board,action)))<v:
                v = maxValue(result(board,action))
                opaction = action

    return opaction

def maxValue(state):
    v=float('-inf')
    if terminal(state):
        return utility(state)
    for action in actions(state):
        v=max(v,minValue(result(state,action)))
    return v


def minValue(state):
    v=float('inf')
    if terminal(state):
        return utility(state)
    for action in actions(state):
        v=min(v,maxValue(result(state,action)))
    return v