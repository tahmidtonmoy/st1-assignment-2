"""SmartCare v0.4: Week 7 domain implementation (Python 3.10+).

SCHEDULED keeps the earlier display value 'Booked'. Specialty is added by
Stage 4. Uniqueness, booking coordination and persistence remain external.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum


def _required_text(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    value = value.strip()
    if not value:
        raise ValueError(f"{field} must not be blank")
    return value


class AppointmentStatus(Enum):
    SCHEDULED = "Booked"
    CANCELLED = "Cancelled"


class InvalidStatusTransition(ValueError):
    """An operation is not allowed from the current appointment status."""


class Patient:
    def __init__(self, patient_id: str, name: str):
        self._patient_id = _required_text(patient_id, "patient_id")
        self._name = _required_text(name, "name")

    @property
    def patient_id(self) -> str:
        return self._patient_id

    @property
    def name(self) -> str:
        return self._name

    def matches_id(self, patient_id: str) -> bool:
        return self.patient_id == patient_id

    def get_history(self, appointments: list[Appointment]) -> list[Appointment]:
        return [a for a in appointments
                if a.patient.patient_id == self.patient_id]


class Practitioner:
    def __init__(self, practitioner_id: str, name: str, specialty: str,
                 recorded_availability: list[datetime] | None = None):
        self._practitioner_id = _required_text(practitioner_id, "practitioner_id")
        self._name = _required_text(name, "name")
        self._specialty = _required_text(specialty, "specialty")
        if recorded_availability is not None:
            if not isinstance(recorded_availability, list):
                raise TypeError("recorded_availability must be a list or None")
            if any(not isinstance(t, datetime) for t in recorded_availability):
                raise TypeError("availability entries must be datetime objects")
        # Copy into an immutable internal sequence; None means unknown.
        self._recorded_availability = (
            None if recorded_availability is None
            else tuple(recorded_availability)
        )

    @property
    def practitioner_id(self) -> str:
        return self._practitioner_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def specialty(self) -> str:
        return self._specialty

    @property
    def recorded_availability(self) -> list[datetime] | None:
        return (None if self._recorded_availability is None
                else list(self._recorded_availability))

    def get_availability(self, day: date) -> list[datetime] | None:
        slots = self.recorded_availability
        return None if slots is None else [t for t in slots if t.date() == day]

    def get_schedule(self, day: date,
                     appointments: list[Appointment]) -> list[Appointment]:
        return [a for a in appointments
                if a.practitioner.practitioner_id == self.practitioner_id
                and a.appointment_time.date() == day]

    def is_booked_at(self, appointment_time: datetime,
                     appointments: list[Appointment]) -> bool:
        return any(a.practitioner.practitioner_id == self.practitioner_id
                   and a.appointment_time == appointment_time
                   and a.is_active() for a in appointments)


class Appointment:
    def __init__(self, appointment_id: str, patient: Patient,
                 practitioner: Practitioner, appointment_time: datetime):
        self._appointment_id = _required_text(appointment_id, "appointment_id")
        self._patient = patient
        self._practitioner = practitioner
        self._appointment_time = appointment_time
        self._status = AppointmentStatus.SCHEDULED
        self.validate()

    @property
    def appointment_id(self) -> str:
        return self._appointment_id

    @property
    def patient(self) -> Patient:
        return self._patient

    @property
    def practitioner(self) -> Practitioner:
        return self._practitioner

    @property
    def appointment_time(self) -> datetime:
        return self._appointment_time

    @property
    def status(self) -> AppointmentStatus:
        return self._status

    def validate(self) -> None:
        _required_text(self.appointment_id, "appointment_id")
        if not isinstance(self.patient, Patient):
            raise TypeError("patient must be a Patient")
        if not isinstance(self.practitioner, Practitioner):
            raise TypeError("practitioner must be a Practitioner")
        _required_text(self.patient.name, "patient.name")
        _required_text(self.practitioner.name, "practitioner.name")
        if not isinstance(self.appointment_time, datetime):
            raise TypeError("appointment_time must be a datetime")
        if not isinstance(self.status, AppointmentStatus):
            raise TypeError("status must be an AppointmentStatus")

    def is_active(self) -> bool:
        return self.status is AppointmentStatus.SCHEDULED

    def cancel(self) -> None:
        if self.status is not AppointmentStatus.SCHEDULED:
            raise InvalidStatusTransition("Only SCHEDULED appointments can be cancelled")
        self._status = AppointmentStatus.CANCELLED
