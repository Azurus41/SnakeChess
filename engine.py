#Pychess engine.py

from piece import *
import time
import colorama
colorama.init()

class Engine:
    """Code du moteur d'échecs"""
    
    def __init__(self):
        self.MAX_PLY = 1000
        self.INFINITY=32000 
        self.pv_length = [0] * self.MAX_PLY
        self.endgame = False
        self.init_depth = 4 # search in fixed depth
        self.nodes = 0 # number of nodes
        self.clear_pv()
        
    def chkCmd(self,c):
        
        """Check if the command 'c' typed by user is like a move,
        i.e. 'e2e4','b7b8n'...
        Returns '' if correct.
        Returns a string error if not.
        """
        
        err=(
        'The move must be 4 or 5 letters : e2e4, b1c3, e7e8q...',
        'Incorrect move.'
        )        
        letters=('a','b','c','d','e','f','g','h')
        numbers=('1','2','3','4','5','6','7','8')
                
        if(len(c)<4 or len(c)>5):
            return err[0]
        
        if(c[0] not in letters):
            return err[1]
            
        if(c[1] not in numbers):
            return err[1]
            
        if(c[2] not in letters):
            return err[1]
            
        if(c[3] not in numbers):
            return err[1]
            
        return ''    
    
    def usermove(self,b,c):
        
        """Move a piece for the side to move, asked in command line.
        The command 'c' in argument is like 'e2e4' or 'b7b8q'.
        Argument 'b' is the chessboard.
        """
        
        if(self.endgame):
            self.print_result(b)
            return        
              
        # Testing the command 'c'. Exit if incorrect.
        chk = self.chkCmd(c)
        if(chk!=''):
            print(chk)
            return
            
        # Convert cases names to int, ex : e3 -> 44
        pos1=b.caseStr2Int(c[0]+c[1])
        pos2=b.caseStr2Int(c[2]+c[3])
        
        # Promotion asked ?
        promote=''
        if(len(c)>4):
            promote=c[4]
            if(promote=='q'):
                promote='q'
            elif(promote=='r'):
                promote='r'
            elif(promote=='n'):
                promote='n'
            elif(promote=='b'):
                promote='b'
            
        # Generate moves list to check 
        # if the given move (pos1,pos2,promote) is correct
        mList=b.gen_moves_list()
        
        # The move is not in list ? or let the king in check ?
        if(((pos1,pos2,promote) not in mList) or (b.domove(pos1,pos2,promote)==False)):
            print("\n"+c+' : incorrect move or let king in check'+"\n")
            self.usermove(self,b,c)
        
    def search(self, b):
        if self.endgame:
            self.print_result(b)
            return

        self.clear_pv()
        self.nodes = 0
        b.ply = 0

        print("ply\ttime\tnodes\tkn/s\tscore\tpv")

        start = time.time()
        for i in range(1, self.init_depth + 1):
            score = self.alphabeta(i, -100, 100, b)
            end = time.time()
            if b.side2move == 'blanc':
                if score >= 0:
                    score_text = colorama.Fore.GREEN + "+" + str(round(score, 2)) + colorama.Fore.WHITE
                else:
                    score_text = colorama.Fore.RED + str(round(score, 2)) + colorama.Fore.WHITE
                print("{}\t{}\t{}\t{}\t{}\t".format(i, round(end - start, 3), self.nodes, round((self.nodes * (1 / round(end - start + 0.001, 3)) / 1000), 2), score_text), end='')
            elif b.side2move == 'noir':
                if score >= 0:
                    score_text = colorama.Fore.GREEN + str(round(-score, 2)) + colorama.Fore.WHITE
                else:
                    score_text = colorama.Fore.RED + "+" + str(round(-score, 2)) + colorama.Fore.WHITE
                print("{}\t{}\t{}\t{}\t{}\t".format(i, round(end - start, 3), self.nodes, round((self.nodes * (1 / round(end - start + 0.001, 3)) / 1000), 2), score_text), end='')

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

        best = self.pv[0][0]
        b.domove(best[0], best[1], best[2])
        b.render()

    def alphabeta(self,depth,alpha,beta,b):
        if(depth==0):
            return b.evaluer()

        self.nodes+=1
        self.pv_length[b.ply] = b.ply

        # Do not go too deep
        if(b.ply >= self.MAX_PLY-1):
            return b.evaluer()

        mList=b.gen_moves_list()

        f=False # flag to know if at least one move will be done
        for i,m in enumerate(mList):
            if(not b.domove(m[0],m[1],m[2])):
                continue
                
            f=True # a move has passed
            
            score=-self.alphabeta(depth-1,-beta,-alpha,b)

            # Unmake move
            b.undomove()

            if(score>alpha):
                if(score>=beta):
                    return beta
                alpha = score

                # Updating the triangular PV-Table
                self.pv[b.ply][b.ply] = m
                j = b.ply + 1
                while(j<self.pv_length[b.ply+1]):
                    self.pv[b.ply][j] = self.pv[b.ply+1][j]
                    self.pv_length[b.ply] = self.pv_length[b.ply + 1]
                    j+=1

        if(not f):
            chk = chk = b.in_check(b.side2move)
            if(chk):
                return -self.INFINITY + b.ply # MAT
            else:
                return 0 # DRAW
        
        if m == b.last_move():
            return 0 # 2 TIME REPETITION

        return alpha

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
                print("1/2-1/2")
            self.endgame = True
            time.sleep(10000)
            
    def clear_pv(self):
        self.pv = [[0 for x in range(self.MAX_PLY)] for x in range(self.MAX_PLY)]