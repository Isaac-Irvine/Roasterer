from random import choice

from job import Job
from person import Person
from slot import Slot


class Roaster:

    def __init__(self):
        self._possible_slots = dict()  # maps people to set of possible slots
        self._assigned_people = dict()  # maps slots to people

    def add_possible_slot(self, person: Person, slot: Slot):
        if person in self._possible_slots:
            self._possible_slots[person].add(slot)
        else:
            self._possible_slots[person] = {slot}

    def assign(self, person: Person, slot: Slot):
        self._assigned_people[slot] = person
        for slots in self._possible_slots.values():
            if slot in slots:
                slots.remove(slot)

    def _get_people_with_least_slots(self) -> set[Person]:
        least_slots = set()
        num = 9999999999
        for person, possible_slots in self._possible_slots.items():
            if len(possible_slots) < num:
                least_slots = {person}
                num = len(possible_slots)
            elif len(possible_slots) == num:
                least_slots.add(person)
        return least_slots

    def _get_slots_with_least_people(self, person: Person) -> set[Slot]:
        least_people = set()
        min_num = 9999999999
        for slot in self._possible_slots[person]:
            num = len(list(filter(lambda p: slot in p, self._possible_slots.values())))
            if num < min_num:
                least_people = {slot}
            elif num == min_num:
                least_people.add(slot)
        return least_people

    def _contains_job(self, job: Job, excluded: Person = None) -> bool:
        for person, slots in self._possible_slots.items():
            if person is excluded:
                continue
            for slot in slots:
                if slot.job is job:
                    return True
        return False

    def fill(self):
        while len(self._possible_slots):
            person = choice(tuple(self._get_people_with_least_slots()))

            if len(self._possible_slots[person]) == 0:
                self._possible_slots.pop(person)
                continue

            slot = choice(tuple(self._get_slots_with_least_people(person)))

            # if the jobs needs a supervisor, make a supervisor job
            # but if nobody can do the supervisor role, remove the role from the person
            if person.needs_supervision(slot.job):
                if not slot.cycle.add_job(slot.job.get_supervisor_job()):
                    self._possible_slots[person].remove(slot)
                    continue

            self.assign(person, slot)

            # avoid doing the same job more than once a roaster
            if self._contains_job(slot.job, person):
                self._possible_slots[person] = set(filter(lambda s: s.job != slot.job, self._possible_slots[person]))

    def to_table(self, cycle_order: list, job_order: list[Job]):
        # add all the jobs that aren't already in jobs_order into it
        # probably just supervisors
        for slot in filter(lambda s: s.job not in job_order, self._assigned_people.keys()):
            for i in range(len(job_order)):
                if slot.job.get_name().startswith(job_order[i].get_name()):
                    job_order.insert(i + 1, slot.job)
                    break
            else:
                job_order.append(slot.job)

        # make a table of all the cycles and jobs
        table = [[''] + [job.get_name() for job in job_order] + ['Spares...']]
        table += [[cycle.get_name()] + [''] * len(job_order) for cycle in cycle_order]

        for slot, person in self._assigned_people.items():
            table[cycle_order.index(slot.cycle) + 1][job_order.index(slot.job) + 1] = person.get_name()

        return table
