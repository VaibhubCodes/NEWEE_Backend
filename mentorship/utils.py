from datetime import timedelta

def generate_slots(availability):
    """
    Generate 30-minute and 60-minute slots from a mentor's availability.

    :param availability: MentorAvailability instance.
    :return: Tuple of (30_min_slots, 60_min_slots).
    """
    start_time = availability.start_time
    end_time = availability.end_time

    # Generate 30-minute slots
    thirty_min_slots = []
    current_time = start_time
    while current_time + timedelta(minutes=30) <= end_time:
        thirty_min_slots.append((current_time, current_time + timedelta(minutes=30)))
        current_time += timedelta(minutes=30)

    # Generate 60-minute slots
    current_time = start_time
    sixty_min_slots = []
    while current_time + timedelta(minutes=60) <= end_time:
        sixty_min_slots.append((current_time, current_time + timedelta(minutes=60)))
        current_time += timedelta(minutes=60)

    return thirty_min_slots, sixty_min_slots


def filter_available_slots(slots, booked_slots):
    """
    Filter out slots that overlap with booked slots.

    :param slots: List of tuples [(start_time, end_time)].
    :param booked_slots: List of tuples [(start_time, end_time)].
    :return: List of available slots.
    """
    available_slots = []
    for slot in slots:
        is_overlapping = any(
            booked_start < slot[1] and slot[0] < booked_end for booked_start, booked_end in booked_slots
        )
        if not is_overlapping:
            available_slots.append(slot)
    return available_slots
