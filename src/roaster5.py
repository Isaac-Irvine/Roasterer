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


def _contains_slot(slots: dict[Person, set[Slot]], slot: Slot, excluded: Person = None) -> bool:
    for person, slots_ in slots.items():
        if person is excluded:
            continue
        if slot in slots_:
            return True
    return False


class Roaster:

    def __init__(self):
        self._possible_slots = dict()  # maps people to set of possible slots. All the slots currently searching
        self._assigned_people = dict()  # maps slots to people
        self._cycles = []
        self._jobs_order = []

        self._multiple_slots = dict()
        self._repeating_slots = dict()
        self._consecutive_slots = dict()
        self._multiple_hard_slots = dict()
        self._repeating_hard_slots = dict()
        self._consecutive_hard_slots = dict()

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

    def _can_assign(self, person: Person, slot: Slot, stop=False):
        # get all slots from everyone except person
        # if slots isn't in this list, then noby else can do it and it can't be assigned
        return (
            _contains_slot(self._possible_slots, slot, person)
            or _contains_slot(self._multiple_slots, slot, person)
            or _contains_slot(self._repeating_slots, slot, person)
            or _contains_slot(self._consecutive_slots, slot, person)
            or _contains_slot(self._multiple_hard_slots, slot, person)
            or _contains_slot(self._repeating_hard_slots, slot, person)
            or _contains_slot(self._consecutive_hard_slots, slot, person)
        )

        other_slots = self._possible_slots[person]
        if person in self._multiple_slots:
            other_slots = other_slots.union(self._multiple_slots[person])
        if person in self._repeating_slots:
            other_slots = other_slots.union(self._repeating_slots[person])
        if person in self._consecutive_slots:
            other_slots = other_slots.union(self._consecutive_slots[person])
        if person in self._multiple_hard_slots:
            other_slots = other_slots.union(self._multiple_hard_slots[person])
        if person in self._repeating_hard_slots:
            other_slots = other_slots.union(self._repeating_hard_slots[person])
        if person in self._consecutive_hard_slots:
            other_slots = other_slots.union(self._consecutive_hard_slots[person])

        if stop:
            pass

        return _contains_slot()

        found = False
        for s in other_slots:
            if s.cycle != slot.cycle or s is slot:
                continue
            found = True
            if (
                _contains_slot(self._possible_slots, s, person)
                or _contains_slot(self._multiple_slots, s, person)
                or _contains_slot(self._repeating_slots, s, person)
                or _contains_slot(self._consecutive_slots, s, person)
                or _contains_slot(self._multiple_hard_slots, s, person)
                or _contains_slot(self._repeating_hard_slots, s, person)
                or _contains_slot(self._consecutive_hard_slots, s, person)
            ):
                return True
        return not found

    def assign(self, person: Person, slot: Slot):
        self._assigned_people[slot] = person

        # don't assign other people the slot # TODO: Find dryer way to do this
        for slots in self._possible_slots.values():
            if slot in slots:
                slots.remove(slot)
        for slots in self._multiple_slots.values():
            if slot in slots:
                slots.remove(slot)
        for slots in self._repeating_slots.values():
            if slot in slots:
                slots.remove(slot)
        for slots in self._consecutive_slots.values():
            if slot in slots:
                slots.remove(slot)
        for slots in self._multiple_hard_slots.values():
            if slot in slots:
                slots.remove(slot)
        for slots in self._repeating_hard_slots.values():
            if slot in slots:
                slots.remove(slot)
        for slots in self._consecutive_hard_slots.values():
            if slot in slots:
                slots.remove(slot)

        # remove other jobs in cycle from person. Person can't do more than one job per cycle
        self._possible_slots[person] = set(filter(lambda s: s.cycle != slot.cycle, self._possible_slots[person]))
        if person in self._multiple_slots:
            self._multiple_slots[person] = set(filter(lambda s: s.cycle != slot.cycle, self._multiple_slots[person]))
        if person in self._repeating_slots:
            self._repeating_slots[person] = set(filter(lambda s: s.cycle != slot.cycle, self._repeating_slots[person]))
        if person in self._consecutive_slots:
            self._consecutive_slots[person] = set(filter(lambda s: s.cycle != slot.cycle, self._consecutive_slots[person]))
        if person in self._multiple_hard_slots:
            self._multiple_hard_slots[person] = set(filter(lambda s: s.cycle != slot.cycle, self._multiple_hard_slots[person]))
        if person in self._repeating_hard_slots:
            self._repeating_hard_slots[person] = set(filter(lambda s: s.cycle != slot.cycle, self._repeating_hard_slots[person]))
        if person in self._consecutive_hard_slots:
            self._consecutive_hard_slots[person] = set(filter(lambda s: s.cycle != slot.cycle, self._consecutive_hard_slots[person]))

        repeating, non_repeating = _split_set(lambda s: s.job == slot.job, self._possible_slots[person])
        consecutive, non_consecutive_repeating = _split_set(lambda s: self._cycles_next_to(s.cycle, slot.cycle), repeating)
        if slot.job.is_hard():
            non_repeating_hard, non_repeating_easy = _split_set(lambda s: s.job.is_hard(), non_repeating)
            consecutive_hard, consecutive_easy = _split_set(lambda s: s.job.is_hard(), consecutive)
            non_consecutive_repeating_hard, non_consecutive_repeating_easy = _split_set(lambda s: s.job.is_hard(), non_consecutive_repeating)
            self._multiple_slots[person] = non_repeating_easy
            self._consecutive_slots[person] = consecutive_easy
            self._repeating_slots[person] = non_consecutive_repeating_easy
            self._multiple_hard_slots[person] = non_repeating_hard
            self._consecutive_hard_slots[person] = consecutive_hard
            self._repeating_hard_slots[person] = non_consecutive_repeating_hard
        else:
            self._multiple_slots[person] = non_repeating
            self._consecutive_slots[person] = consecutive
            self._repeating_slots[person] = non_consecutive_repeating

        self._possible_slots[person] = set()

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
                min_num = num
            elif num == min_num:
                least_people.append(slot)
        return least_people

    def fill(self):
        while self._possible_slots:
            self._fill()

            if self._multiple_slots:
                self._possible_slots = self._multiple_slots
                self._multiple_slots = dict()
            elif self._repeating_slots:
                self._possible_slots = self._repeating_slots
                self._repeating_slots = dict()
            elif self._consecutive_slots:
                self._possible_slots = self._consecutive_slots
                self._consecutive_slots = dict()
            elif self._multiple_hard_slots:
                self._possible_slots = self._multiple_hard_slots
                self._multiple_hard_slots = dict()
            elif self._repeating_hard_slots:
                self._possible_slots = self._repeating_hard_slots
                self._repeating_hard_slots = dict()
            elif self._consecutive_hard_slots:
                self._possible_slots = self._consecutive_hard_slots
                self._consecutive_hard_slots = dict()

    def _assign_compolsery(self):
        to_assign = set()
        for person, slots in self._possible_slots.items():
            for s in slots:
                if not self._can_assign(person, s):
                    print(f'has to assign {s} to {person}')
                    to_assign.add((person, s))
        for person, slot in to_assign:
            self.assign(person, slot)
        if to_assign:
            self._assign_compolsery()  # I know this is a sin but I am in a rush. tbh that logic appies to everything in this program. I'm so so sorry to whoever has to maintaing this

    def _fill(self):
        while len(self._possible_slots):
            self._assign_compolsery()
            person = choice(self._get_people_with_least_slots())

            if len(self._possible_slots[person]) == 0:
                self._possible_slots.pop(person)
                continue

            self.print_table()

            slot = choice(self._get_slots_with_least_people(person))

            print(f'trying to assign {person} {slot}')

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
