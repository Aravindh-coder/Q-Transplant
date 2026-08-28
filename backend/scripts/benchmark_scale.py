"""Generate deterministic synthetic donor rows for matching benchmarks; no medical decisions are made."""
import argparse, json, random, time

def run(n):
    random.seed(42)
    start=time.perf_counter()
    counts={"ACTIVE":0,"INACTIVE":0}
    for _ in range(n): counts[random.choice(tuple(counts))]+=1
    elapsed=time.perf_counter()-start
    return {"records":n,"generation_seconds":elapsed,"counts":counts,"seed":42}

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--size",type=int,default=1000); a=p.parse_args()
    print(json.dumps(run(a.size),indent=2))
