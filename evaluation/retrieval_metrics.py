def retrieval_precision(retrieved, relevant):
    if not retrieved: return 0.0
    return len(set(retrieved)&set(relevant))/len(retrieved)

def retrieval_recall(retrieved, relevant):
    if not relevant: return 0.0
    return len(set(retrieved)&set(relevant))/len(set(relevant))

def recall_at_k(relevant_ids,retrieved_ids,k):
    return retrieval_recall(retrieved_ids[:k], relevant_ids)

def precision_at_k(relevant_ids,retrieved_ids,k):
    if k <= 0: return 0.0
    return len(set(relevant_ids)&set(retrieved_ids[:k]))/k
