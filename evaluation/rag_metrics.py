def context_relevance(context, question):
    if not context or not question: return 0.0
    q=set(question.lower().split()); c=set(context.lower().split())
    return len(q & c)/max(len(q),1)

def answer_relevance(answer, expected):
    if not answer or not expected: return 0.0
    if answer.strip().casefold() == expected.strip().casefold(): return 1.0
    a=set(answer.lower().split()); e=set(expected.lower().split())
    return len(a&e)/max(len(e),1)
