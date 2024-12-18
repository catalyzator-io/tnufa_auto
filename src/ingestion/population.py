from typing import Any, Protocol

class DatabasePopulatorProtocol(Protocol):
    def populate(self, data: Any):
        ...

class DatabasePopulator:
    def populate(self, data: Any):
        ...