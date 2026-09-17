"""Week 6 SmartCare v0.3 domain skeletons.

Constructors store state only. Business operations deliberately remain stubs.
IDs, Booked/Cancelled and availability-slot representation are provisional.
No booking, persistence, interface or reporting workflow is implemented.
"""
from __future__ import annotations
from datetime import date, datetime


class Patient:
    def __init__(self, patient_id: str, name: str):
        self.patient_id = patient_id
        self.name = name

    def matches_id(self, patient_id: str) -> bool:
        """FR-02: report whether this record has the requested identifier."""
        raise NotImplementedError("Stage 3 skeleton only")

    def get_history(self, appointments: list[Appointment]) -> list[Appointment]:
        """FR-11: select this patient's appointments, including cancellations."""
        raise NotImplementedError("Stage 3 skeleton only")


class Practitioner:
    def __init__(self, practitioner_id: str, name: str,
                 recorded_availability: list[datetime] | None = None):
        self.practitioner_id = practitioner_id
        self.name = name
        self.recorded_availability = recorded_availability

    def get_availability(self, day: date) -> list[datetime] | None:
        """FR-05: return recorded slots; None means availability is unknown."""
        raise NotImplementedError("Stage 3 skeleton only")

    def get_schedule(self, day: date,
                     appointments: list[Appointment]) -> list[Appointment]:
        """FR-08: select this practitioner's appointments for the date."""
        raise NotImplementedError("Stage 3 skeleton only")

    def is_booked_at(self, appointment_time: datetime,
                     appointments: list[Appointment]) -> bool:
        """FR-07: check an exact-time active booking, not interval overlap."""
        raise NotImplementedError("Stage 3 skeleton only")


class Appointment:
    def __init__(self, appointment_id: str, patient: Patient,
                 practitioner: Practitioner, appointment_time: datetime,
                 status: str = "Booked"):
        self.appointment_id = appointment_id
        self.patient = patient
        self.practitioner = practitioner
        self.appointment_time = appointment_time
        self.status = status

    def validate(self) -> None:
        """FR-03: validate names, required references and date/time state."""
        raise NotImplementedError("Stage 3 skeleton only")

    def is_active(self) -> bool:
        """FR-07/A3: determine whether this status blocks the exact slot."""
        raise NotImplementedError("Stage 3 skeleton only")

    def cancel(self) -> None:
        """FR-09/10: change status; preserve identity, links and time."""
        raise NotImplementedError("Stage 3 skeleton only")
