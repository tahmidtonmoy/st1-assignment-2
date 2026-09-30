"""Storage contract owned by the application, independent of storage technology."""
from abc import ABC, abstractmethod
from domain.models import Appointment


class AppointmentRepository(ABC):
    """Single-process contract; reads return detached appointment snapshots.

    add rejects duplicate IDs; save requires an existing ID. A failed write
    must leave stored state unchanged. Neither operation checks booking rules.
    """

    @abstractmethod
    def add(self, appointment: Appointment) -> None:
        """Insert a new ID; raise ValueError if that ID already exists."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, appointment_id: str) -> Appointment | None:
        """Return a detached snapshot, or None when no record matches."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Appointment]:
        """Return detached snapshots, including cancelled appointments."""
        raise NotImplementedError

    @abstractmethod
    def save(self, appointment: Appointment) -> None:
        """Replace an existing ID; raise LookupError if it does not exist."""
        raise NotImplementedError
