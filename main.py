# Pychess main.py

from board import *
from engine import *

b = Board()
e = Engine()

while True:
    e.search(b)
    b.showHistory()
    e.print_result(b)