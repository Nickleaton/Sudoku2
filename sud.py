import argparse
import os

from sudoku import Sudoku


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Solve Sudoku')
    parser.add_argument('-p', '--problem', type=str)
    args = parser.parse_args()
    s = Sudoku.load(os.path.join('tests', args.problem + ".yaml"))
    s.problem.writeLP(os.path.join('mlp', args.problem + ".mlp"))
    s.solve()
    s.html(os.path.join('html', args.problem + ".html"))
