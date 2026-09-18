def exact_match(prediction, expected): return float(prediction.strip()==expected.strip())
def mean(values): return sum(values)/len(values) if values else 0.0
