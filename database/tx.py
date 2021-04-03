
class Tx:
    
    def __init__(self, *, from_acc: str, to_acc: str, value: int, data: str):
        self._from_acc = from_acc
        self._to_acc = to_acc
        self._value = value
        self._data = data

    @property
    def from_acc(self) -> str:
        return self._from_acc

    @property
    def to_acc(self) -> str:
        return self._to_acc

    @property
    def value(self) -> int:
        return self._value

    @property
    def data(self) -> str:
        return self._data

    @property
    def is_reward(self) -> str:
        return self.data == "reward"

    @classmethod
    def init_from_json(cls, j: dict):
        return cls(
            from_acc=j["from"],
            to_acc=j["to"],
            value=j["value"],
            data=j["data"]
        )

    def to_json(self):
        return {
            "from": self.from_acc,
            "to": self.to_acc,
            "value": self.value,
            "data": self.data
        }