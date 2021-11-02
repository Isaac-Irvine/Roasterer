
from random import choice

from cycle import Cycle
from job import Job
from person import Person
from roaster import Roaster


class Slot:
    def __init__(self, cycle: Cycle, job: Job):
        self.job = job
        self.cycle = cycle


def _get_least_slots(slots: dict[Person, set[Slot]]):
    """
    Find the slot with the lest cells assigned
    """
    min_slots = next(iter(slots))
    for slot in slots:
        if len(slots[min_slots]) > len(slots[slot]):
            min_slots = slot
    return min_slots


def _get_number_of_cells(slot: Slot, slots: dict[Person, set[Slot]]) -> int:
    num = 0
    for person in slots:
        for s in slots[person]:
            if s is slot:
                num += 1
    return num


def _get_least_available_slot(slots: dict[Person, set[Slot]], person: Person):
    min_slot = None
    min_num = 99999999
    for slot in slots[person]:
        num = _get_number_of_cells(slot, slots)
        if num < min_num:
            min_slot = slot
            min_num = num
    return min_slot


def _get_all_slots(roaster: Roaster) -> dict[Person, set[Slot]]:
    slots = {}
    for cycle in roaster.get_cycles():
        for person in cycle.get_spare_people():
            if person not in slots:
                slots[person] = set()
        for job in cycle.get_spare_jobs():
            slot = Slot(cycle, job)
            for person in cycle.get_spare_people():
                if person.can_do_job(job):
                    slots[person].add(slot)
    return slots


def _contains_job(slots: dict[Person, set[Slot]], job, excluded) -> bool:
    for person in slots:
        if person is excluded:
            continue
        for slot in slots[person]:
            if slot.job is job:
                return True
    return False


def fill_roaster(roaster: Roaster) -> Roaster:
    slots = _get_all_slots(roaster)

    # assign slots
    while len(slots) != 0:
        person = _get_least_slots(slots)
        if len(slots[person]) == 0:
            slots.pop(person)
            continue
        #slot = choice(list(slots[person]))
        slot = _get_least_available_slot(slots, person)
        slot.cycle.assign(slot.job, person)
        if person.needs_supervision(slot.job):
            supervisors_slot = Slot(slot.cycle, slot.job.get_supervisor_job())
            slot.cycle.add_job(supervisors_slot.job)
            for potential_supervisor in slot.cycle.get_spare_people():
                if potential_supervisor.can_do_job(supervisors_slot.job):
                    if person not in slots:
                        slots[person] = set()
                    slots[potential_supervisor].add(supervisors_slot)

        for p in slots:
            if slot in slots[p]:
                slots[p].remove(slot)

        # don't do more than one job per cycle
        slots[person] = set(filter(lambda s: s.cycle != slot.cycle, slots[person]))

        # avoid doing more than one hard job per roaster
        if slot.job.is_hard() and _contains_job(slots, slot.job, person):
            slots[person] = set(filter(lambda s: s.job != slot.job, slots[person]))

        # avoid doing the same job more than once a roaster
        if _contains_job(slots, slot.job, person):
            slots[person] = set(filter(lambda s: s.job != slot.job, slots[person]))

        if len(slots[person]) == 0:
            slots.pop(person)

    return roaster
