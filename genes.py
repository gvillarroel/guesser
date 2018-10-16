import random
import operator

LOCALS = "__locals__"
GLOBALS = "__globals__"

MAX_IDENT = 4


class Gen(object):
    GEN_ALLOWS = {}

    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        self.output_type = None
        self.input_type = None
        self.ident = ident
        self.sample = sample
        self.cause_ident = False
        self.s_locals = s_locals
        self.s_globals = s_globals

    def __repr__(self):
        return "Not yet:%s" % type(self)

    def __str__(self):
        return self.__repr__()

    def eval(self, data, v_local=locals(), v_global=globals()):
        pass

    def random_child(self, but=None):
        c_list = self.GEN_ALLOWS if not but else list(set(self.GEN_ALLOWS) - but)
        sel = random.choice(c_list)
        new_g = sel(self.sample
                    , ident=self.ident + (1 * self.cause_ident)
                    , s_locals=self.s_locals, s_globals=self.s_globals)
        while new_g.cause_ident and self.ident > MAX_IDENT:
            sel = random.choice(self.GEN_ALLOWS)
            new_g = sel(self.sample
                    , ident=self.ident + (1 * self.cause_ident)
                    , s_locals=self.s_locals, s_globals=self.s_globals)

        return new_g


class Crom(Gen):
    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        Gen.__init__(self, sample, ident, s_locals, s_globals)
        self.cause_ident = True
        self.gens = [self.random_child()]

    def __repr__(self):

        return """def fun(record):
%s%s
        """ % ("\t" * (self.ident + (self.cause_ident * 1)), "\n".join([e.__repr__() for e in self.gens]))

    def mutate(self):
        if not random.randint(0, 100):
            croms = filter(lambda x: isinstance(x, Crom), self.gens)
            if croms:
                random.choice(croms).mutate()
            else:
                self.gens.append(self.random_child())
        else:
            # self.gens.append(self.random_child())
            self.gens = [self.random_child()]
        # TODO: update output_type

    def eval(self, data, v_local=locals(), v_global=globals()):
        l = {}
        r = None
        for gen in self.gens:
            r = gen.eval(data, l, v_global)
        return r


class G_Sum(Gen):

    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        Gen.__init__(self, sample, ident, s_locals, s_globals)
        self.cause_ident = True
        self.gen = self.random_child()

    def __repr__(self):
        return "sum(%s)" % self.gen

    def eval(self, data, v_local=locals(), v_global=globals()):
        return sum(self.gen.eval(data, v_global=v_global))


class G_Assing(Gen):
    genetic_base = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __repr__(self):
        return "%s = %s" % (self.variable_name, self.gen)

    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        Gen.__init__(self, sample, ident, s_locals, s_globals)
        self.variable_name = "".join(random.sample(self.genetic_base, random.randint(1, 10)))

    def eval(self, data, v_local=locals(), v_global=globals()):
        l = {}
        v_local[self.variable_name] = self.gen.eval(data, l, v_global)


class G_Access_By_Key(Gen):
    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        Gen.__init__(self, sample, ident, s_locals, s_globals)
        self.variable_name = random.choice(sample.keys())
        while self.variable_name[0] == "_":
            self.variable_name = random.choice(sample.keys())
            self.output_type = type(sample[self.variable_name])

    def __repr__(self):
        return "[%s]" % self.variable_name

    def eval(self, data, v_local=locals(), v_global=globals()):
        return data[self.variable_name]


class G_Access_To_Local_Variable(Gen):
    key = LOCALS

    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        Gen.__init__(self, sample, ident, s_locals, s_globals)
        if self.key not in sample or not sample[self.key]:
            raise Exception("No local variables")
            # try another door

        self.variable_name = random.choice(sample[self.key].keys())
        self.output_type = type(sample[self.key][self.variable_name])

    def __repr__(self):
        return "%s" % self.variable_name

    def eval(self, data, v_local=locals(), v_global=globals()):
        return v_local[self.variable_name]


class G_Access_To_Global_Variable(G_Access_To_Local_Variable):
    key = GLOBALS

    def eval(self, data, v_local=locals(), v_global=globals()):
        return v_global[self.variable_name]


class G_List_All_Values_Of_Dict(Gen):
    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        Gen.__init__(self, sample, ident, s_locals, s_globals)
        max_length = random.randint(0, len(sample.keys()) - 1)
        self.keys = list(map(str, random.sample(sample.keys(), max(2, len(sample.keys())))))

    def __repr__(self):
        return "[e for e in %s]" % self.keys

    def eval(self, data, v_local=locals(), v_global=globals()):
        return [data[key] for key in self.keys]


class G_Minus(Gen):
    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        Gen.__init__(self, sample, ident, s_locals, s_globals)
        self.gen1 = self.random_child()
        self.gen2 = self.random_child()

    def eval(self, data, v_local=locals(), v_global=globals()):
        return self.gen1 - self.gen2


# , operator.concat, operator.contains
# , operator.countOf, operator.indexOf,
# , operator.mod
# , operator.or_
# operator.lt, operator.le, operator.eq
#                  , operator.ne, operator.ge, operator.gt
#                  , operator.is_, operator.is_not,
# , operator.and_,
MAP_OP = {
    operator.add : '+'
    , operator.mul : '*'
    , operator.sub : '-'
    , operator.truediv : '/'
}
class G_Int_Operator(Gen):
    OPERATORS = MAP_OP.keys()
    def __repr__(self):
        return "(%s %s %s)" % (self.gen1, MAP_OP[self.op], self.gen2)

    def __init__(self, sample, ident=0, s_locals=locals(), s_globals=globals()):
        Gen.__init__(self, sample, ident, s_locals, s_globals)
        self.cause_ident = True
        self.gen1 = self.random_child() if ident < 2 else self.random_child({G_Int_Operator, })
        self.gen2 = self.random_child() if ident < 2 else self.random_child({G_Int_Operator, })
        self.op = random.choice(self.OPERATORS)

    def eval(self, data, v_local=locals(), v_global=globals()):
        try:
            return self.op(self.gen1.eval(data, v_local, v_global)
                           , self.gen2.eval(data, v_local, v_global))
        except:
            self.op = random.choice(self.OPERATORS)
            return self.eval(data, v_local, v_global)


Crom.GEN_ALLOWS = (G_Int_Operator, )
G_Sum.GEN_ALLOWS = (G_List_All_Values_Of_Dict,)
G_Int_Operator.GEN_ALLOWS = (G_Int_Operator, G_Access_By_Key)
