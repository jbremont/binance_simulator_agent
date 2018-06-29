import re

#0v1# JC  June  6, 2018  Initial setup

class A(object):
    def __init__(self):
        return

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()




