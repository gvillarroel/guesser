import random, sys, json
random.seed(10)
# python math_gen.py out.tsv 10
# bash -c "python math_gen.py out.tsv 100; head out.tsv"
def method(record):
    return record["a"] + record["b"] - record["c"]

def dat():
    return {
        "a": random.randint(1,1000),
        "b": random.randint(1,1000),
        "c": random.randint(1,1000)
    }

def gen(path, limit):
    with open(path, "w") as output:
        for s in range(limit):
            args = dat()
            args["result"] = method(args)
            output.write(json.dumps(args) + "\n")

if __name__ == "__main__":
    path = sys.argv[1]
    limit = int(sys.argv[2])
    gen(path, limit)
