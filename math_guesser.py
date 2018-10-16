import random
import json
import operator
from genes import *


class MathGuesser:

    def mutate(self):
        self.me.mutate()

    @property
    def fitness(self):
        f = 0
        l, g = {}, globals()
        for val in self.targets:
            if len(val) == 2:
                d,v = val
                v2 = self.me.eval(d, l, g)
                if v == v2:
                    f += 1
        return f

    def __init__(self, targets, parents=[]):
        # type: (tuple[dict,str], tuple[MathGuesser]) -> None
        self.targets = targets
        if parents:
            if len(parents) > 1:
                self.me = combine(parents)
                self.mutate()
            else:
                self.me = parents[0].me
                self.mutate()
        else:
            self.me = Crom(random.choice(self.targets)[0])

    def __repr__(self):
        return "%s" % self.me


def combine(parents):
    # type: (tuple[MathGuesser]) -> str
    return [random.choice(parents)[i] for i in range(0, len(parents[0]))]


def extract_data(line):
    e = json.loads(line)
    r = e["result"]
    del e["result"]
    return (e, r, )

def guesser(target):
    targets = []
    with open(target, "r") as f:
        targets = list(map(extract_data, f.readlines()))
    print "using %s samples" % len(targets)
    parent = MathGuesser(targets)
    tries = 1000
    while parent.fitness != len(targets) and tries :
        tries -= 1
        child = MathGuesser(target, (parent,))
        toleranse = 20
        while toleranse:
            toleranse -= 1
            child.mutate()
            if parent.fitness < child.fitness:
                break
        if child.fitness <= parent.fitness:
            continue
        parent = child
        if parent.fitness == len(targets):
            break
        break
    print "="*30
    print parent
    print "="*30
    print "fitness:", parent.fitness

    print "found"