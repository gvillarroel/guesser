import random

class StringGuesser:

    genetic_base = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!."

    def mutate(self):
        self.me[random.choice(range(len(self)))] = random.choice(StringGuesser.genetic_base)

    @property
    def fitness(self):
        return sum(1 for expected, actual in zip(self.target, self.me) if expected == actual)

    def generate_base(self):
        return random.sample(StringGuesser.genetic_base, len(self.target))

    def __init__(self, target, parents=[]):
        # type: (str, tuple[StringGuesser]) -> None
        self.target = target
        if parents:
            if len(parents) > 1:
                self.me = combine(parents)
                self.mutate()
            else:
                self.me = list(parents[0].me)
                self.mutate()
        else:
            self.me  = self.generate_base()
            self.mutate()

    def __add__(self, other):
        return self.me + other.me

    def __len__(self):
        return len(self.me)

    def __repr__(self):
        return "%s\t%s\t%s" % ("".join(self.me), self.fitness, self.target)

    def __getitem__(self, item):
        return self.me[item]

def combine(parents):
    # type: (tuple[StringGuesser]) -> str
    return [random.choice(parents)[i] for i in range(0, len(parents[0]))]


def guesser(target):
    parent = StringGuesser(target)
    while True:
        child = StringGuesser(target, (parent,))
        if child.fitness <= parent.fitness:
            continue
        parent = child
        if parent.fitness == len(target):
            break
        print parent
    print "found"
    print parent

