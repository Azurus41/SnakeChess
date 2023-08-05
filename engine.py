#Pychess engine.py

from piece import *
import time
import colorama
colorama.init()

class Engine:
    """Code du moteur d'échecs"""
    
    def __init__(self):
        self.MAX_PLY = 32
        self.pv_length = [0] * self.MAX_PLY
        self.endgame = False
        self.init_depth = 4 # search in fixed depth
        self.nodes = 0 # number of nodes
        self.clear_pv()
        
    def search(self, b):
        if self.endgame:
            self.print_result(b)
            return

        self.clear_pv()
        self.nodes = 0
        b.ply = 0

        print("ply\ttime\tnodes\tkn/s\tscore\tpv")
        sorted_moves = self.sort_captures(b.gen_moves_list())

        start = time.time()
        for i in range(1, self.init_depth + 1):
            score = self.alphabeta(i, -100, 100, b)
            end = time.time()
            if b.side2move == 'blanc':
                if score >= 0:
                    score_text = colorama.Fore.GREEN + str(round(score, 2)) + colorama.Fore.WHITE
                else:
                    score_text = colorama.Fore.RED + str(round(score, 2)) + colorama.Fore.WHITE
                print("{}\t{}\t{}\t{}\t{}\t".format(i, round(end - start, 3), self.nodes, round((self.nodes * (1 / round(end - start, 3)) / 1000), 2), score_text), end='')
            elif b.side2move == 'noir':
                if score >= 0:
                    score_text = colorama.Fore.GREEN + str(round(-score, 2)) + colorama.Fore.WHITE
                else:
                    score_text = colorama.Fore.RED + str(round(-score, 2)) + colorama.Fore.WHITE
                print("{}\t{}\t{}\t{}\t{}\t".format(i, round(end - start, 3), self.nodes, round((self.nodes * (1 / round(end - start, 3)) / 1000), 2), score_text), end='')

            j = 0
            while self.pv[j][j] != 0:
                c = self.pv[j][j]
                pos1 = b.caseInt2Str(c[0])
                pos2 = b.caseInt2Str(c[1])
                print("{}{}{}".format(pos1, pos2, c[2]), end=' ')
                j += 1
            print()
            
            if score > 100 or score < -100:
                break

        time.sleep(4)
        best = self.pv[0][0]
        b.domove(best[0], best[1], best[2])
        b.render()
        self.print_result(b)

    def alphabeta(self, depth, alpha, beta, b):
        if depth == 0:
            return b.evaluer()

        self.nodes += 1
        self.pv_length[b.ply] = b.ply

        chk = b.in_check(b.side2move)
        if chk:
            depth += 1

        last_move_capture = False  # Variable to keep track if the last move was a capture
        
        best_score = -100
        pv_move = None

        sorted_moves = self.sort_captures(b.gen_moves_list())
        for move in sorted_moves:
            if not b.domove(move[0], move[1], move[2]):
                continue

            last_move_capture = move[2] is not None
            score = -self.alphabeta(depth - 1, -beta, -alpha, b)
            b.undomove()

            if score > best_score:
                best_score = score
                pv_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        if pv_move is not None:
            self.pv[b.ply][b.ply] = pv_move

        if last_move_capture:
            depth += 1
        
        if not sorted_moves:
            if chk:
                return -self.INFINITY + b.ply
            else:
                return 0

        return best_score

    def sort_captures(self, moves_list):
        captures = [move for move in moves_list if move[2] is not None]
        non_captures = [move for move in moves_list if move[2] is None]
        return captures + non_captures

    def print_result(self, b):
        f = False
        for pos1, pos2, promote in b.gen_moves_list():
            if b.domove(pos1, pos2, promote):
                b.undomove()
                f = True
                break

        if not f:
            if b.in_check(b.side2move):
                print("0-1 {Black mates}" if b.side2move == 'blanc' else "1-0 {White mates}")
            else:
                print("1/2-1/2 {Stalemate}")
            self.endgame = True
            time.sleep(10000)
            
    def clear_pv(self):
        self.pv = [[0 for x in range(self.MAX_PLY)] for x in range(self.MAX_PLY)]