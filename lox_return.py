
class LoxReturn(RuntimeError):

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value