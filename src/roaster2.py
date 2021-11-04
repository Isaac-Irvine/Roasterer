from random import choice

from tabulate import tabulate

from job import Job
from person import Person
from slot import Slot


def _split_set(func, the_set: set):
    set_1, set_2 = set(), set()
    for item in the_set:
        if func(item):
            set_1.add(item)
        else:
            set_2.add(item)
    return set_1, set_2


def _split_slots(func, slots):
    slots_1, slots_2 = dict(), dict()
    for person in slots:
        set_1, set_2 = set(), set()
        for slot in slots[person]:
            if func(slot, person):
                set_1.add(slot)
            else:
                set_2.add(slot)
        if set_1:
            slots_1[person] = set_1
        if set_2:
            slots_2[person] = set_2
    return slots_1, slots_2


class Roaster:

    def __init__(self):
        self._possible_slots = dict()  # maps people to set of possible slots. All the slots currently searching
        self._assigned_people = dict()  # maps people to slots
        self._remaining_slots = dict()
        self._cycles = []
        self._jobs_order = []

    def _cycles_next_to(self, cycle_1, cycle_2):
        return abs(self._cycles.index(cycle_1) - self._cycles.index(cycle_2)) == 1

    def add_cycle(self, cycle):
        """
        For cycles to add themselves to the roaster
        """
        self._cycles.append(cycle)

    def set_jobs_order(self, jobs_order):
        self._jobs_order = jobs_order

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
        for slots in self._remaining_slots.values():
            if slot in slots:
                slots.remove(slot)



        self._remaining_slots[person] = self._possible_slots[person]
        self._possible_slots.pop(person)

    def _get_people_with_least_slots(self) -> list[Person]:
        least_slots = []
        min_num = 9999999999
        for person, possible_slots in self._possible_slots.items():
            num = len(list(filter(lambda s: not person.needs_supervision(s.job), possible_slots)))
            if num < min_num:
                least_slots = [person]
                min_num = num
            if num == min_num:
                least_slots.append(person)
        return least_slots

    def _get_slots_with_least_people(self, person: Person) -> list[Slot]:
        least_people = []
        min_num = 9999999999
        for slot in self._possible_slots[person]:
            num = len(list(filter(lambda p: slot in p, self._possible_slots.values())))
            if num < min_num:
                least_people = [slot]
            elif num == min_num:
                least_people.append(slot)
        return least_people

    def _contains_job(self, job: Job, excluded: Person = None) -> bool:
        for person, slots in self._possible_slots.items():
            if person is excluded:
                continue
            for slot in slots:
                if slot.job is job:
                    return True
        return False

    def split_repeating(self):
        all_non_repeating, all_repeating = set(), set()
        for person, slot in self._assigned_people.items():
            repeating, non_repeating = _split_set(lambda s: s.job == slot.job, self._remaining_slots[person])
            all_non_repeating = all_non_repeating.union(non_repeating)
            all_repeating = all_repeating.union(repeating)
        return all_non_repeating, all_repeating

    def fill(self):
        # for slots in _split_slots(lambda s, p: s.job.is_hard(), self._possible_slots):
        while self._possible_slots:
            self.print_table()
            self._fill()

            #no_repeat, repeat = self.split_repeating()
            #self._possible_slots = no_repeat

    def _fill(self):
        while len(self._possible_slots):
            person = choice(self._get_people_with_least_slots())
            slot = choice(self._get_slots_with_least_people(person))

            # if the jobs needs a supervisor, make a supervisor job
            # but if nobody can do the supervisor role, remove the role from the person
            if person.needs_supervision(slot.job):
                if not slot.cycle.add_job(slot.job.get_supervisor_job()):
                    self._possible_slots[person].remove(slot)
                    continue

            self.assign(person, slot)

    def _has_job(self, person, cycle=None):
        for slot, p in self._assigned_people.items():
            if p is person:
                if cycle is not None and slot.cycle is not cycle:
                    continue
                return True
        return False

    def print_table(self):
        print(tabulate(self.to_table(), headers='firstrow'))

    def to_table(self):
        # add all the jobs that aren't already in jobs_order into it
        # probably just supervisors
        for slot in filter(lambda s: s.job not in self._jobs_order, self._assigned_people.keys()):
            for i in range(len(self._jobs_order)):
                if slot.job.get_name().startswith(self._jobs_order[i].get_name()):
                    self._jobs_order.insert(i + 1, slot.job)
                    break
            else:
                self._jobs_order.append(slot.job)

        # get spares
        spares = []
        for cycle in self._cycles:
            spares_this_cycle = []
            for person in cycle.get_people():
                if not self._has_job(person, cycle):
                    spares_this_cycle.append(person.get_name())
            spares.append(spares_this_cycle)

        max_spares = 0
        for cycle in spares:
            max_spares = max(max_spares, len(cycle))

        table = []
        table.append(
            ['']
            + [job.get_name() for job in self._jobs_order]
            + ['Spares...']
            + [''] * max(0, max_spares - 1)
        )
        for i, cycle in enumerate(self._cycles):
            table.append(
                [cycle.get_name()]
                + [''] * len(self._jobs_order)
                + spares[i]
                + [''] * min(1, max_spares - len(spares[i]))
            )

        # make a table of all the cycles and jobs
        for slot, person in self._assigned_people.items():
            table[self._cycles.index(slot.cycle) + 1][self._jobs_order.index(slot.job) + 1] = person.get_name()

        return table
