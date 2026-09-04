"""
Part G - the one controlled improvement, and Part F - verification.

This is task_1_enhanced.py with exactly one change: book_appointment now
refuses a booking when the requested practitioner is already booked at
that time. Everything else is unchanged.
"""

appointments = []


# ---------------------------------------------------------------------
# PART G - THE ONE CONTROLLED IMPROVEMENT (new)
# ---------------------------------------------------------------------

def is_practitioner_busy(practitioner_name, appointment_time):
    """Return True if this practitioner already has a booking at this time."""
    for appointment in appointments:
        if (appointment["practitioner"] == practitioner_name
                and appointment["time"] == appointment_time):
            return True
    return False


def book_appointment(patient_name, practitioner_name, appointment_time):
    if not patient_name:                                    # unchanged
        raise ValueError("Patient name cannot be empty")    # unchanged

    # >>> the one improvement - new in v0.1 <<<
    if is_practitioner_busy(practitioner_name, appointment_time):
        raise ValueError(
            f"{practitioner_name} already has an appointment at {appointment_time}"
        )
    # >>> end of the improvement <<<

    appointment = {                                         # unchanged
        "patient": patient_name,
        "practitioner": practitioner_name,
        "time": appointment_time
    }
    appointments.append(appointment)                        # unchanged


def display_appointments():                                 # unchanged
    if not appointments:
        print("No appointments recorded.")
        return
    for appointment in appointments:
        print(f"Patient: {appointment['patient']} | "
              f"Practitioner: {appointment['practitioner']} | "
              f"Time: {appointment['time']}")


# ---------------------------------------------------------------------
# PART F - VERIFY BEHAVIOUR
# Four tests, matching the four scenarios listed in the lab handout.
# ---------------------------------------------------------------------

def run_verification_tests():
    print("\n--- Part F: verification ---")

    # Test 1 - normal appointment (expected: accepted)
    try:
        book_appointment('Carol Nguyen', 'Dr. John Doe', '2024-07-20 02:00 PM')
        print("Test 1 normal appointment      -> PASS (accepted)")
    except ValueError as error:
        print(f"Test 1 normal appointment      -> FAIL ({error})")

    # Test 2 - blank patient name (expected: rejected)
    try:
        book_appointment('', 'Dr. Jane Roe', '2024-07-20 03:00 PM')
        print("Test 2 blank patient name      -> FAIL (empty name accepted)")
    except ValueError as error:
        print(f"Test 2 blank patient name      -> PASS (rejected: {error})")

    # Test 3 - same practitioner and time twice (expected: rejected)
    try:
        book_appointment('David Lee', 'Dr. John Doe', '2024-07-20 10:00 AM')
        print("Test 3 duplicate booking       -> FAIL (double booking accepted)")
    except ValueError as error:
        print(f"Test 3 duplicate booking       -> PASS (rejected: {error})")

    # Test 4 - strange input: None values
    try:
        book_appointment(None, 'Dr. Jane Roe', '2024-07-20 04:00 PM')
        print("Test 4a patient_name = None    -> FAIL (None accepted)")
    except ValueError as error:
        print(f"Test 4a patient_name = None    -> PASS (rejected: {error})")

    try:
        book_appointment('Emma Wilson', 'Dr. Jane Roe', None)
        print("Test 4b appointment_time = None -> KNOWN GAP (accepted; "
              "the time is never validated)")
    except ValueError as error:
        print(f"Test 4b appointment_time = None -> rejected: {error}")


if __name__ == "__main__":
    print("Welcome to SmartCare: The Clinical Appointment Booking System!")
    book_appointment('Alice Smith', 'Dr. John Doe', '2024-07-20 10:00 AM')
    book_appointment('Bob Johnson', 'Dr. Jane Roe', '2024-07-20 11:30 AM')
    display_appointments()

    run_verification_tests()

    print("\n--- Final appointment list ---")
    display_appointments()