#!/opt/homebrew/Caskroom/miniforge/base/envs/torch/bin/python
import sys
from scripts.download import entrypoint

if __name__ == '__main__':
    sys.exit(entrypoint())