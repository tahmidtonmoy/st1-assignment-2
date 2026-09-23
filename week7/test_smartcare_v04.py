"""Reproducible Week 7 behaviour checks. Run: python test_smartcare_v04.py"""
from datetime import datetime, timedelta
import unittest

from smartcare_v04 import (
    Patient, Practitioner, Appointment, AppointmentStatus, InvalidStatusTransition,
)


class DomainChecks(unittest.TestCase):
    def setUp(self):
        self.time = datetime(2026, 9, 28, 10, 0)
        self.patient = Patient("P001", "Alex Green")
        self.practitioner = Practitioner("PR001", "Dr Lee", "General practice")
        self.appointment = Appointment("A001", self.patient, self.practitioner, self.time)

    def test_01_valid_objects(self):
        self.appointment.validate()
        self.assertIs(self.appointment.patient, self.patient)
        self.assertIs(self.appointment.practitioner, self.practitioner)
        self.assertIs(self.appointment.status, AppointmentStatus.SCHEDULED)
        self.assertEqual(self.appointment.status.value, "Booked")
        self.assertTrue(self.appointment.is_active())

    def test_02_patient_validation(self):
        for pid, name in [("", "Alex"), ("P001", "   ")]:
            with self.subTest(pid=pid, name=name), self.assertRaises(ValueError):
                Patient(pid, name)
        with self.assertRaises(TypeError):
            Patient("P001", None)
        self.assertEqual(Patient(" P001 ", " Alex ").name, "Alex")

    def test_03_practitioner_validation(self):
        for args in [(" ", "Dr Lee", "GP"), ("PR001", "", "GP"),
                     ("PR001", "Dr Lee", " ")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Practitioner(*args)
        with self.assertRaises(TypeError):
            Practitioner("PR001", "Dr Lee", 123)
        with self.assertRaises(TypeError):
            Practitioner("PR001", "Dr Lee", "GP", ["Monday"])
        with self.assertRaises(TypeError):
            Practitioner("PR001", "Dr Lee", "GP", "Monday")

    def test_04_appointment_validation(self):
        with self.assertRaises(ValueError):
            Appointment(" ", self.patient, self.practitioner, self.time)
        for patient, practitioner, when in [
            (None, self.practitioner, self.time),
            (self.patient, "Dr Lee", self.time),
            (self.patient, self.practitioner, "2026-09-28 10:00 AM"),
            (self.patient, self.practitioner, None),
        ]:
            with self.subTest(patient=patient, when=when), self.assertRaises(TypeError):
                Appointment("A002", patient, practitioner, when)

    def test_05_cancel_preserves_record(self):
        a = self.appointment
        before = (a.appointment_id, a.patient, a.practitioner, a.appointment_time)
        a.cancel()
        self.assertIs(a.status, AppointmentStatus.CANCELLED)
        self.assertFalse(a.is_active())
        self.assertEqual(before, (a.appointment_id, a.patient, a.practitioner,
                                  a.appointment_time))

    def test_06_repeated_cancel_rejected(self):
        self.appointment.cancel()
        with self.assertRaises(InvalidStatusTransition):
            self.appointment.cancel()
        self.assertIs(self.appointment.status, AppointmentStatus.CANCELLED)

    def test_07_public_state_is_read_only(self):
        attempts = [(self.patient, "name", ""), (self.patient, "patient_id", "X"),
                    (self.practitioner, "practitioner_id", "X"),
                    (self.practitioner, "name", ""),
                    (self.practitioner, "specialty", ""),
                    (self.practitioner, "recorded_availability", []),
                    (self.appointment, "status", AppointmentStatus.CANCELLED),
                    (self.appointment, "appointment_id", "X"),
                    (self.appointment, "patient", None),
                    (self.appointment, "practitioner", None),
                    (self.appointment, "appointment_time", "")]
        for obj, field, value in attempts:
            with self.subTest(field=field), self.assertRaises(AttributeError):
                setattr(obj, field, value)
        self.assertTrue(self.appointment.is_active())

    def test_08_history_retains_cancelled_and_matches_identity(self):
        self.appointment.cancel()
        other = Appointment("A002", Patient("P002", "Sam"), self.practitioner, self.time)
        records = [self.appointment, other]
        history = Patient("P001", "Alex Green").get_history(records)
        self.assertEqual(history, [self.appointment])
        history.clear()
        self.assertEqual(len(records), 2)
        self.assertTrue(self.patient.matches_id("P001"))
        self.assertFalse(self.patient.matches_id("P999"))

    def test_09_schedule_filters_practitioner_and_day(self):
        other_day = Appointment("A002", self.patient, self.practitioner,
                                self.time + timedelta(days=1))
        other_practitioner = Practitioner("PR002", "Dr Khan", "GP")
        other = Appointment("A003", self.patient, other_practitioner, self.time)
        self.appointment.cancel()
        records = [self.appointment, other_day, other]
        self.assertEqual(self.practitioner.get_schedule(self.time.date(), records),
                         [self.appointment])

    def test_10_exact_active_slot_check(self):
        records = [self.appointment]
        self.assertTrue(self.practitioner.is_booked_at(self.time, records))
        self.assertFalse(self.practitioner.is_booked_at(self.time + timedelta(minutes=1), records))
        self.assertFalse(Practitioner("PR002", "Dr Khan", "GP").is_booked_at(self.time, records))
        self.appointment.cancel()
        self.assertFalse(self.practitioner.is_booked_at(self.time, records))

    def test_11_unknown_and_empty_availability(self):
        self.assertIsNone(self.practitioner.get_availability(self.time.date()))
        p = Practitioner("PR002", "Dr Khan", "GP", [])
        self.assertEqual(p.get_availability(self.time.date()), [])

    def test_12_availability_is_defensively_copied(self):
        slots = [self.time, self.time + timedelta(days=1)]
        p = Practitioner("PR002", "Dr Khan", "GP", slots)
        slots.clear()
        self.assertEqual(len(p.recorded_availability), 2)
        exposed = p.recorded_availability
        exposed.clear()
        self.assertEqual(p.get_availability(self.time.date()), [self.time])
        self.assertEqual(len(p.recorded_availability), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
