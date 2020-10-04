import yaml
from pulp import COIN_CMD
from Sudoku import Sudoku
import argparse

config = yaml.safe_load(open('config.yaml', 'r'))
solver = COIN_CMD(**config)

HTML_TEMPLATE = """ \
<?xml version="1.0" encoding="UTF-8"?> 
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
    <html>
        <head>
        <title>Sudoku</title>
    </head>
    <body>
    <h1>Description</h1>
    <h1>Rules</h1>
    $rules
    <h1>Board</h1>
    $svg
    <h1>Solution</h1>
    $solution
    </body>
</html>
"""


s = Sudoku.load('tests/problem011.yaml')
s.problem.writeLP('mps/problem011.mlp')
s.solve()
s.html("html/problem011.html")
