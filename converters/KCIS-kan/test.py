def hello(n):
    if n==6:
        return True
    return False

def increment(n):
    yield n+1
    yield n+2
    yield n+3



for x in [0]+ increment(3):
    print(x)
