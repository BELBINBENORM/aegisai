from evaluation.metrics import exact_match

def run_case(answer, expected): return {"exact_match": exact_match(answer, expected)}
def run(dataset): return [run_case(x["answer"],x["expected"]) for x in dataset]

def evaluate_answers(actual_answers):
    expected={"q1":"Python is a programming language.","q2":"RAG combines retrieval with generation to answer using external context.","q3":"An AI agent can reason, use tools, and perform tasks."}
    return {k: {"score": 1 if actual_answers.get(k,"").strip().casefold()==v.casefold() else 0} for k,v in expected.items()}

def build_report(results):
    vals=[v.get("score",0) if isinstance(v,dict) else 0 for v in results.values()]
    total=len(vals); passed=sum(vals); return {"total_questions":total,"passed":passed,"failed":total-passed,"accuracy":passed/total if total else 0.0}
