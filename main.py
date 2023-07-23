# Pychess main.py

# Import object classes
from board import *
from engine import *
import time

b=Board()
e=Engine()

while(True):
    e.search(b)