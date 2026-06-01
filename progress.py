import sys


def tick(message: str = "") -> None:
    if message:
        print(f"\n{message} ", end="", flush=True)
    else:
        print("*", end="", flush=True)


def done() -> None:
    print(" done", flush=True)
