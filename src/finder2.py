
from random import choice

from cycle import Cycle
from job import Job
from person import Person
from roaster import Roaster


class Slot:
    def __init__(self, cycle: Cycle, job: Job):
        self._job = job
        self._cycle = cycle

    def get_cycle(self) -> Cycle:
        return self._cycle

    def get_job(self) -> Job:
        return self._job


def _get_least_slots(slots: dict[Person, set[Slot]]):
    """
    Find the slot with the lest cells assigned
    """
    min_slots = next(iter(slots))
    for slot in slots:
        if len(slots[min_slots]) > len(slots[slot]):
            min_slots = slot
    return min_slots


def fill_roaster(roaster: Roaster) -> Roaster:
    # get list of who can do what slots
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

    # assign slots
    while len(slots) != 0:
        person = _get_least_slots(slots)
        if len(slots[person]) == 0:
            slots.pop(person)
            continue
        slot = choice(list(slots[person]))
        #print(f'assigning {person.get_name()} to {slot.get_job().get_name()} in {slot.get_cycle().get_name()}')
        slot.get_cycle().assign(slot.get_job(), person)

        for p in slots:
            if slot in slots[p]:
                slots[p].remove(slot)

        slots[person] = set(filter(lambda s: s.get_cycle() != slot.get_cycle(), slots[person]))

        if len(slots[person]) == 0:
            slots.pop(person)

    return roaster
