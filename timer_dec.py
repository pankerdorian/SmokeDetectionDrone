def timer(func):
    import time

    def inner(*args, **kwargs):
        t = time.time()
        res = func(*args, **kwargs)
        time_took = time.time() - t
        print(f"timer ended {func.__name__}: {time_took}")
        return res

    return inner
