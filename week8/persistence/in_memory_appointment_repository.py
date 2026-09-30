"""In-memory storage adapter. Records do not survive process restart."""
from copy import deepcopy
from domain.models import Appointment
from repositories.appointment_repository import AppointmentRepository


class InMemoryAppointmentRepository(AppointmentRepository):
    def __init__(self):
        self._appointments: dict[str, Appointment] = {}

    def add(self, appointment: Appointment) -> None:
        key = appointment.appointment_id
        if key in self._appointments:
            raise ValueError(f"Appointment ID {key} already exists")
        self._appointments[key] = deepcopy(appointment)

    def get_by_id(self, appointment_id: str) -> Appointment | None:
        return deepcopy(self._appointments.get(appointment_id))

    def list_all(self) -> list[Appointment]:
        return deepcopy(list(self._appointments.values()))

    def save(self, appointment: Appointment) -> None:
        key = appointment.appointment_id
        if key not in self._appointments:
            raise LookupError(f"Appointment {key} was not found")
        self._appointments[key] = deepcopy(appointment)
