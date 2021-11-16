from slot import Slot, PotentialSlots
from job import Job
from person import Person


class Cycle:
    def __init__(self, number: int):
        self._number = number
        self._slots = PotentialSlots()
        self.available_people = set()
        self.casually_available_people = set()

    def add_job(self, job: Job, available_for_training: bool = False):
        """
        Adds a job to the roaster in this cycle.
        """
        slot = Slot(self, job, available_for_training)
        self._slots.add_slot(slot)
        for person in self._slots.get_people():
            if person.can_do_job(job) and (available_for_training or not person.needs_supervision(job)):
                self._slots.add_potential_person(slot, person)

    def add_person(self, person: Person, casual: bool):
        if casual:
            self.casually_available_people.add(person)
        else:
            self.available_people.add(person)

        self._slots.add_person(person)
        for slot in self._slots.get_slots():
            if (
                not person.can_do_job(slot.job)
                or (not slot.available_for_training and person.needs_supervision(slot.job))
                or (casual and not slot.job.is_casual())
            ):
                continue
            self._slots.add_potential_person(slot, person)

    def get_potential_slots(self) -> PotentialSlots:
        return self._slots

    def get_people(self) -> set[Person]:
        return self._slots.get_people()

    def get_available(self) -> set[Person]:
        return self.available_people

    def get_casually_available(self) -> set[Person]:
        return self.casually_available_people

    def get_name(self) -> str:
        return f'Cycle {self._number}'

    def __repr__(self) -> str:
        return f'Cycle {self._number}'

    def get_number(self):
        return self._number

    def next_to(self, cycle: 'Cycle'):
        return abs(cycle._number - self._number) == 1
