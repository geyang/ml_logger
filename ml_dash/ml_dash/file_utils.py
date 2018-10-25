def path_match(query, pattern):
    import glob, re
    regex = fnmatch.translate(pattern)
    reobj = re.compile(regex)
    return reobj.match(query)
