def compress(chunks,max_chars=10000):
    out=[]; total=0
    for c in chunks:
        if total+len(c.content)>max_chars: break
        out.append(c); total+=len(c.content)
    return out


def compress_context(chunks, max_chars=10000):
    return "\n\n".join(c.content for c in compress(chunks, max_chars=max_chars))
