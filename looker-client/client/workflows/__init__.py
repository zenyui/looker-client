
registry = []

class Workflow():
    def __init__(self, register_function):
        self.register = register_function
        registry.append(self)

from . import delete_users
