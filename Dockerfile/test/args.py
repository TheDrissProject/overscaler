import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python import overtools as ot
import subprocess

def main():
    ot.get_args()
if __name__ == '__main__':
    main()
