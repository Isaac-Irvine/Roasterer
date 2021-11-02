from functools import reduce

from roaster2 import Roaster
from slot import Slot
from job import Job
from person import Person


class Cycle:
    def __init__(self, name: str, roaster: Roaster):
        self._name = name
        self._slots = set()
        self._people = set()
        self._roaster = roaster

    def get_people(self) -> set[Person]:
        return self._people

    def get_slots(self):
        return self._slots

    def add_job(self, job: Job, available_for_training: bool):
        slot = Slot(self, job, available_for_training)
        self._slots.add(slot)
        for person in self._people:
            if person.can_do_job(job) and (available_for_training or not person.needs_supervision(job)):
                self._roaster.add_possible_slot(person, slot)

    def add_person(self, person):
        self._people.add(person)
        for slot in self._slots:
            if person.can_do_job(slot.job) and (slot.available_for_training or not person.needs_supervision(slot.job)):
                self._roaster.add_possible_slot(person, slot)

    def get_name(self):
        return self._name

    def __str__(self):
        return self._name


