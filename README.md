# SnakeChess
# Chess engine in python
# Run main.py to test it

# Capacities:
# - Play a whole game against himself until mate (or bugged draw)
# - show ASCII chessboard
# - show ply, nodes, pv (bugged)
# - Use material and PESTO tables for estimate position

# To-Do list:
# - solve all bugs
# - Add transposition table, endgame table and opening table
# - Surely other things but idk why for the moment

# Bugs:
# - pv bugged (2 times Nc3 in the pv of starting position at ply 4)
# - draw by repetition even when one of the sides is winning
# - (not a bug) but it is verrrrrry slow
