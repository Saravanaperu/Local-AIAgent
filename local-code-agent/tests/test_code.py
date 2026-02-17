def hello_world():
    """Prints hello world."""
    print("Hello, world!")

class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}"
