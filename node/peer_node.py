
class PeerNode:
    
    def __init__(self, *, ip: str, port: int, is_bootstrap: bool, is_active: bool):
        self._ip = ip
        self._port = port
        self._is_bootstrap = is_bootstrap
        self._is_active = is_active

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port

    @property
    def url(self) -> str:
        return f"http://{self.ip}:{self.port}"

    @property
    def is_bootstrap(self) -> bool:
        return self._is_bootstrap

    @property
    def is_active(self) -> bool:
        return self._is_active

    def to_json(self) -> dict:
        return {
            "ip": self.ip,
            "port": self.port,
            "is_bootstrap": self.is_bootstrap,
            "is_active": self.is_active
        }

    @classmethod
    def from_json(cls, j: dict):
        return cls(
            ip=j.get('ip'),
            port=j.get('port'),
            is_bootstrap=j.get('is_bootstrap'),
            is_active=j.get('is_active')
        )