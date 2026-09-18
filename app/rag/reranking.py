def rerank(query,chunks,limit=6):
    terms=set(query.lower().split())
    return sorted(chunks,key=lambda c:sum(t in c.content.lower() for t in terms),reverse=True)[:limit]
