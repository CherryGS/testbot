import functools
import time


def coolen(times):
    def decorator(func):
        lst = 0

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal lst
            r = time.time()
            if r - lst < times:
                print("cooling down!")
            else:
                lst = r
                return func(*args, **kwargs)

        return wrapper

    return decorator


@coolen(5)
def test():
    print(" ---- ")


test()
test()
time.sleep(5)
test()
