from random import choice

from person import Person
from slot import Slot


class Roaster:

    def __init__(self):
        self._possible_slots = dict()  # maps people to set of possible slots
        self._assigned_people = dict()  # maps slots to people

    def add_possible_slot(self, person: Person, slot: Slot):
        self._possible_slots[person].add(slot)

    def assign(self, person: Person, slot: Slot):
        self._assigned_people[slot] = person
        for i in self._possible_slots.values():
            if slot in i:
                i.remove(slot)

    def _get_people_with_least_slots(self) -> set[Person]:
        least_slots = set()
        num = 9999999999
        for person, possible_slots in self._possible_slots:
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
            num = len(list(filter(lambda p: slot in p.values(), self._possible_slots)))
            if num < min_num:
                least_people = {slot}
            elif num == min_num:
                least_people.add(slot)
        return least_people

    def fill(self):
        num = 0
        for i in self._possible_slots.values():
            num += len(i)
        print(f'number of things f{num}')

        while len(self._possible_slots):
            person = choice(tuple(self._get_people_with_least_slots()))
            slot = choice(tuple(self._get_slots_with_least_people(person)))

            self.assign(person, slot)

            if person.needs_supervision(slot.job):
                pass  # TODO

    def to_table(self, cycle_order, job_order):
        # add all the jobs that aren't already in jobs_order into it
        # probably just supervisors
        for job in filter(lambda j: j not in job_order, self._assigned_people.keys()):
            for i in range(len(job_order)):
                if job.get_name().startswith(job_order[i].get_name()):
                    job_order.insert(i + 1, job)
                    break
            else:
                job_order.append(job)

        # make a table of all the cycles and jobs
        table = [[''] + [job.get_name() for job in job_order] + ['Spares...']]
        for cycle in cycle_order:
            row = [cycle.get_name()] + [''] * len(job_order)
            for slot in cycle.get_slots():
                if slot in self._assigned_people:
                    row[job_order.index(slot.job) + 1] = self._assigned_people[slot].get_name()
            #for person in cycle.get_spare_people():
            #    row.append(person.get_name())
            table.append(row)

        return table
