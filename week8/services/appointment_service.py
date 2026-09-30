"""Coordinate use cases through the repository contract and domain operations."""
from datetime import date, datetime
from domain.models import Appointment, Patient, Practitioner
from repositories.appointment_repository import AppointmentRepository


class AppointmentService:
    def __init__(self, repository: AppointmentRepository):
        self._repository = repository

    def book(self, appointment_id: str, patient: Patient,
             practitioner: Practitioner, appointment_time: datetime) -> Appointment:
        # The domain validates the candidate before any write occurs.
        appointment = Appointment(appointment_id, patient, practitioner, appointment_time)
        if practitioner.is_booked_at(appointment_time, self._repository.list_all()):
            raise ValueError("Practitioner already has an active appointment at this time")
        self._repository.add(appointment)
        return appointment

    def cancel(self, appointment_id: str) -> Appointment:
        appointment = self.find(appointment_id)
        if appointment is None:
            raise LookupError(f"Appointment {appointment_id} was not found")
        appointment.cancel()  # Appointment owns the transition rule.
        self._repository.save(appointment)
        return appointment

    def find(self, appointment_id: str) -> Appointment | None:
        return self._repository.get_by_id(appointment_id)

    def list_appointments(self) -> list[Appointment]:
        return self._repository.list_all()

    def patient_history(self, patient: Patient) -> list[Appointment]:
        return patient.get_history(self._repository.list_all())

    def practitioner_schedule(self, practitioner: Practitioner,
                              day: date) -> list[Appointment]:
        return practitioner.get_schedule(day, self._repository.list_all())
