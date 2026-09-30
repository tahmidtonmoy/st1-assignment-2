"""Console input, parsing and messages; no storage or booking-rule implementation."""
from datetime import datetime
from domain.models import Appointment, Patient, Practitioner
from services.appointment_service import AppointmentService


TIME_FORMAT = "%Y-%m-%d %I:%M %p"


def format_appointment(appointment: Appointment) -> str:
    return (f"{appointment.appointment_id} | {appointment.patient.name} | "
            f"{appointment.practitioner.name} | "
            f"{appointment.appointment_time.strftime(TIME_FORMAT)} | "
            f"{appointment.status.value}")


def run(service: AppointmentService, patients: dict[str, Patient],
        practitioners: dict[str, Practitioner]) -> None:
    print("SmartCare v0.5 - in-memory demonstration")
    print("Patients: " + ", ".join(patients))
    print("Practitioners: " + ", ".join(practitioners))
    while True:
        try:
            choice = input("1 Book | 2 Cancel | 3 List | 4 Find | 0 Exit: ").strip()
            if choice == "0":
                return
            if choice == "1":
                appointment_id = input("Appointment ID: ").strip()
                patient_id = input("Patient ID: ").strip()
                practitioner_id = input("Practitioner ID: ").strip()
                patient = patients.get(patient_id)
                practitioner = practitioners.get(practitioner_id)
                if patient is None or practitioner is None:
                    print("Patient or practitioner ID was not found.")
                    continue
                when = datetime.strptime(input("Time (YYYY-MM-DD hh:mm AM/PM): ").strip(),
                                         TIME_FORMAT)
                appointment = service.book(appointment_id, patient, practitioner, when)
                print("Booked: " + format_appointment(appointment))
            elif choice == "2":
                appointment = service.cancel(input("Appointment ID: ").strip())
                print("Cancelled: " + format_appointment(appointment))
            elif choice == "3":
                appointments = service.list_appointments()
                if not appointments:
                    print("No appointments.")
                for appointment in appointments:
                    print(format_appointment(appointment))
            elif choice == "4":
                appointment = service.find(input("Appointment ID: ").strip())
                print("Appointment not found." if appointment is None
                      else format_appointment(appointment))
            else:
                print("Choose 0, 1, 2, 3 or 4.")
        except (ValueError, TypeError, LookupError) as error:
            print(f"Unable to complete request: {error}")
        except (EOFError, KeyboardInterrupt):
            print("Goodbye.")
            return
