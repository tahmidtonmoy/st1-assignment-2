from datetime import datetime, timedelta
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import ast
import unittest
from domain.models import Patient, Practitioner, Appointment, AppointmentStatus, InvalidStatusTransition
from repositories.appointment_repository import AppointmentRepository
from persistence.in_memory_appointment_repository import InMemoryAppointmentRepository
from services.appointment_service import AppointmentService
from presentation.console import run


class ServiceChecks(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryAppointmentRepository()
        self.service = AppointmentService(self.repo)
        self.patient = Patient('P001', 'Alex')
        self.practitioner = Practitioner('PR001', 'Dr Lee', 'General practice')
        self.time = datetime(2026, 10, 5, 10)

    def book(self, aid='A001', when=None):
        return self.service.book(aid, self.patient, self.practitioner, when or self.time)

    def test_13_booking_stored_and_retrievable(self):
        a = self.book()
        stored = self.service.find('A001')
        self.assertEqual(stored.patient.patient_id, 'P001')
        self.assertIs(stored.status, AppointmentStatus.SCHEDULED)
        self.assertIsNot(stored, a)

    def test_14_conflict_rejected_before_write(self):
        self.book()
        with self.assertRaises(ValueError): self.book('A002')
        self.assertEqual(len(self.repo.list_all()), 1)
        self.assertIsNone(self.service.find('A002'))

    def test_15_duplicate_id_does_not_overwrite(self):
        self.book()
        with self.assertRaises(ValueError): self.book('A001', self.time + timedelta(hours=1))
        self.assertEqual(self.service.find('A001').appointment_time, self.time)

    def test_16_invalid_booking_does_not_write(self):
        for patient, when in [(None, self.time), (self.patient, 'bad time')]:
            with self.subTest(patient=patient), self.assertRaises(TypeError):
                self.service.book('A001', patient, self.practitioner, when)
        self.assertEqual(self.repo.list_all(), [])

    def test_17_cancel_retains_history_and_frees_slot(self):
        self.book()
        self.service.cancel('A001')
        self.book('A002')
        history = self.service.patient_history(self.patient)
        self.assertEqual([(a.appointment_id, a.status.value) for a in history],
                         [('A001', 'Cancelled'), ('A002', 'Booked')])
        old = self.service.find('A001')
        self.assertEqual((old.patient.patient_id, old.practitioner.practitioner_id,
                          old.appointment_time), ('P001', 'PR001', self.time))

    def test_18_repeat_cancel_keeps_saved_state(self):
        self.book()
        self.service.cancel('A001')
        with self.assertRaises(InvalidStatusTransition): self.service.cancel('A001')
        self.assertIs(self.service.find('A001').status, AppointmentStatus.CANCELLED)
        self.assertEqual(len(self.repo.list_all()), 1)

    def test_19_missing_appointment(self):
        self.assertIsNone(self.service.find('MISSING'))
        with self.assertRaises(LookupError): self.service.cancel('MISSING')
        self.assertEqual(self.repo.list_all(), [])

    def test_20_schedule_filters_after_repository_reads(self):
        self.book()
        self.book('A002', self.time + timedelta(days=1))
        other = Practitioner('PR002', 'Dr Khan', 'GP')
        self.service.book('A003', self.patient, other, self.time)
        result = self.service.practitioner_schedule(self.practitioner, self.time.date())
        self.assertEqual([a.appointment_id for a in result], ['A001'])

    def test_21_exact_time_rule_is_unchanged(self):
        self.book()
        self.book('A002', self.time + timedelta(minutes=1))
        self.assertEqual(len(self.repo.list_all()), 2)

    def test_22_failed_save_leaves_stored_state_unchanged(self):
        self.book()
        with patch.object(self.repo, 'save', side_effect=OSError('write failed')):
            with self.assertRaises(OSError): self.service.cancel('A001')
        self.assertIs(self.repo.get_by_id('A001').status, AppointmentStatus.SCHEDULED)

    def test_23_service_accepts_another_contract_implementation(self):
        class ListRepository(AppointmentRepository):
            def __init__(self): self.rows = []
            def add(self, a):
                if self.get_by_id(a.appointment_id) is not None: raise ValueError('Duplicate ID')
                self.rows.append(deepcopy(a))
            def get_by_id(self, aid):
                return next((deepcopy(a) for a in self.rows if a.appointment_id == aid), None)
            def list_all(self): return deepcopy(self.rows)
            def save(self, a):
                for i, old in enumerate(self.rows):
                    if old.appointment_id == a.appointment_id:
                        self.rows[i] = deepcopy(a)
                        return
                raise LookupError('Missing ID')
        self.service = AppointmentService(ListRepository())
        self.book()
        self.assertIs(self.service.cancel('A001').status, AppointmentStatus.CANCELLED)
        self.assertEqual(len(self.service.list_appointments()), 1)


class RepositoryChecks(unittest.TestCase):
    def test_24_detached_snapshots_require_explicit_save(self):
        repo = InMemoryAppointmentRepository()
        a = Appointment('A001', Patient('P001', 'Alex'),
                        Practitioner('PR001', 'Dr Lee', 'GP'), datetime(2026, 10, 5, 10))
        repo.add(a)
        a.cancel()
        self.assertTrue(repo.get_by_id('A001').is_active())
        snapshot = repo.list_all()[0]
        snapshot.cancel()
        self.assertTrue(repo.get_by_id('A001').is_active())
        repo.save(snapshot)
        self.assertFalse(repo.get_by_id('A001').is_active())

    def test_25_save_requires_existing_record(self):
        repo = InMemoryAppointmentRepository()
        a = Appointment('A001', Patient('P001', 'Alex'),
                        Practitioner('PR001', 'Dr Lee', 'GP'), datetime(2026, 10, 5, 10))
        with self.assertRaises(LookupError): repo.save(a)
        self.assertEqual(repo.list_all(), [])


class BoundaryChecks(unittest.TestCase):
    def test_26_import_direction_and_domain_purity(self):
        root = Path(__file__).resolve().parents[1]
        forbidden = {'domain': {'services', 'repositories', 'persistence', 'presentation', 'sqlite3'},
                     'services': {'persistence', 'presentation', 'sqlite3'},
                     'repositories': {'services', 'persistence', 'presentation', 'sqlite3'},
                     'persistence': {'services', 'presentation'},
                     'presentation': {'repositories', 'persistence', 'sqlite3'}}
        for layer, denied in forbidden.items():
            for path in (root/layer).glob('*.py'):
                for node in ast.walk(ast.parse(path.read_text())):
                    if isinstance(node, ast.Import): imports = [a.name.split('.')[0] for a in node.names]
                    elif isinstance(node, ast.ImportFrom): imports = [(node.module or '').split('.')[0]]
                    else: imports = []
                    self.assertFalse(set(imports) & denied, str(path))
                    if layer != 'presentation' and isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        self.assertNotIn(node.func.id, {'input', 'print'}, str(path))

    def test_27_console_runs_booking_and_cancellation(self):
        service = AppointmentService(InMemoryAppointmentRepository())
        answers = ['1', 'A001', 'P001', 'PR001', '2026-10-05 10:00 AM', '2', 'A001', '3', '0']
        output = StringIO()
        with patch('builtins.input', side_effect=answers), redirect_stdout(output):
            run(service, {'P001': Patient('P001', 'Alex')},
                {'PR001': Practitioner('PR001', 'Dr Lee', 'GP')})
        self.assertIn('Booked: A001', output.getvalue())
        self.assertIn('Cancelled: A001', output.getvalue())
        self.assertIs(service.find('A001').status, AppointmentStatus.CANCELLED)

    def test_28_console_rejects_invalid_time_without_write(self):
        service = AppointmentService(InMemoryAppointmentRepository())
        answers = ['1', 'A001', 'P001', 'PR001', 'invalid', '0']
        output = StringIO()
        with patch('builtins.input', side_effect=answers), redirect_stdout(output):
            run(service, {'P001': Patient('P001', 'Alex')},
                {'PR001': Practitioner('PR001', 'Dr Lee', 'GP')})
        self.assertIn('Unable to complete request:', output.getvalue())
        self.assertEqual(service.list_appointments(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
