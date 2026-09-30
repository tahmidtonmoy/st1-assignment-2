"""Composition root: construct dependencies and launch the console."""
from domain.models import Patient, Practitioner
from persistence.in_memory_appointment_repository import InMemoryAppointmentRepository
from presentation.console import run
from services.appointment_service import AppointmentService


def main() -> None:
    repository = InMemoryAppointmentRepository()
    service = AppointmentService(repository)
    patients = {"P001": Patient("P001", "Alex Green"),
                "P002": Patient("P002", "Sam Brown")}
    practitioners = {"PR001": Practitioner("PR001", "Dr Lee", "General practice"),
                     "PR002": Practitioner("PR002", "Dr Khan", "General practice")}
    run(service, patients, practitioners)


if __name__ == "__main__":
    main()
