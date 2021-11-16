from typing import Callable

from job import Job
from person import Person
from collections import OrderedDict


class Slot:
    def __init__(self, cycle, job: Job, available_for_training: bool):
        self.job: Job = job
        self.cycle: 'Cycle' = cycle
        self.available_for_training: bool = available_for_training

    def __repr__(self) -> str:
        return f'{self.cycle.get_name()} {self.job.get_name()}'


class PotentialSlots:
    def __init__(self):
        self._people_to_slots: dict[Person, set[Slot]] = dict()
        self._slots_to_people: dict[Slot, set[Person]] = dict()
        self._cycles: dict['Cycle', set[Slot]] = dict()

    def get_people(self) -> set[Person]:
        return set(self._people_to_slots.keys())

    def get_slots(self) -> set[Slot]:
        return set(self._slots_to_people.keys())

    def get_slot(self, job: Job, cycle: 'Cycle') -> Slot:
        for slot in self._slots_to_people:
            if slot.job is job and slot.cycle is cycle:
                return slot

    def get_people_for_slot(self, slot: Slot) -> set[Person]:
        return self._slots_to_people[slot]

    def get_slots_for_person(self, person: Person) -> set[Slot]:
        return self._people_to_slots[person]

    def add_slot(self, slot: Slot):
        if slot not in self._slots_to_people:
            self._slots_to_people[slot] = set()
            if slot.cycle not in self._cycles:
                self._cycles[slot.cycle] = {slot}
            else:
                self._cycles[slot.cycle].add(slot)

    def add_person(self, person: Person):
        if person not in self._people_to_slots:
            self._people_to_slots[person] = set()

    def remove_slot(self, slot: Slot):
        for person in self._slots_to_people[slot]:
            self._people_to_slots[person].remove(slot)
        self._slots_to_people[slot].clear()

    def filter_slots_from_people(self, func: Callable[[Slot], bool], person: Person):
        new_slots = set(filter(func, self._people_to_slots[person]))
        for slot in self._people_to_slots[person].difference(new_slots):
            self._slots_to_people[slot].remove(person)
        self._people_to_slots[person] = new_slots

    def add_potential_person(self, slot: Slot, person: Person):
        self._slots_to_people[slot].add(person)
        self._people_to_slots[person].add(slot)

    def _get_people_with_least_slots(self, slot: Slot) -> set[Person]:
        """
        Out of the people who could take the given slot, gets the ones with the least other possible slots
        """
        least_slots = set()
        min_num = float('inf')
        for person in self._slots_to_people[slot]:
            num = len(self._people_to_slots[person])
            if num == 0:
                continue
            if num < min_num:
                least_slots = {person}
                min_num = num
            elif num == min_num:
                least_slots.add(person)
        return least_slots

    def _get_slots_with_least_people(self) -> list[Slot]:
        """
        Goes through all the unassigned slots and gets the ones with the least potential people
        """
        least_people = set()
        min_num = float('inf')
        for slot, people in self._slots_to_people.items():
            if len(people) == 0:
                continue
            if len(people) < min_num:
                least_people = [slot]
                min_num = len(people)
            elif len(people) == min_num:
                least_people.append(slot)
        return least_people

    def get_best_slots(self) -> dict[Slot, set[Person]]:
        slots = dict()
        least_people_slots = self._get_slots_with_least_people()
        for s in least_people_slots:
            slots[s] = self._get_people_with_least_slots(s)
        return slots

    def has_remaining_slots(self):
        return sum(map(len, self._slots_to_people.values())) != 0

    def union(self, other: 'PotentialSlots') -> 'PotentialSlots':
        new = PotentialSlots()

        new._people_to_slots = dict()
        for person, slots in (*self._people_to_slots.items(), *other._people_to_slots.items()):
            if person not in new._people_to_slots:
                new._people_to_slots[person] = set()
            new._people_to_slots[person].update(slots)

        new._slots_to_people = dict()
        for slot, people in (*self._slots_to_people.items(), *other._slots_to_people.items()):
            if slot not in new._slots_to_people:
                new._slots_to_people[slot] = set()
            new._slots_to_people[slot].update(people)

        new._cycles = dict()
        for cycle, slots in (*self._cycles.items(), *other._cycles.items()):
            if cycle not in new._cycles:
                new._cycles[cycle] = set()
            new._cycles[cycle].update(slots)

        return new

    def copy(self):
        new = PotentialSlots()
        for slot, people in self._slots_to_people.items():
            new._slots_to_people[slot] = people.copy()
        for person, slots in self._people_to_slots.items():
            new._people_to_slots[person] = slots.copy()
        for cycle, slots in self._cycles.items():
            new._cycles[cycle] = slots.copy()
        return new

    def try_filter_slots(self, conditions: list[Callable[[Slot, Slot], bool]], person: Person, assigned_slots: dict[Slot, Person]):
        for condition in conditions:
            slots: dict[int, set[Slot]] = dict()
            for potential_slot in self._people_to_slots[person]:
                num = 0
                for assigned_slot, assigned_person in assigned_slots.items():
                    if assigned_person is person and condition(potential_slot, assigned_slot):
                        num += 1
                if num in slots:
                    slots[num].add(potential_slot)
                else:
                    slots[num] = {potential_slot}

            slot_nums = list(slots.keys())
            slot_nums.sort()

            # remove all slots then add them back as needed
            num_of_slots = len(list(filter(lambda i: i, self._slots_to_people.values())))

            for slot in self._people_to_slots[person].copy():
                self._slots_to_people[slot].remove(person)
                self._people_to_slots[person].remove(slot)

            for num in slot_nums:
                if (
                        num != 0
                        and len(list(filter(lambda i: i, self._slots_to_people.values()))) == num_of_slots
                        and self.can_fill()  # conditions[:conditions.index(condition)]
                ):
                    break
                for slot in slots[num]:
                    self._slots_to_people[slot].add(person)
                    self._people_to_slots[person].add(slot)

            for num in slot_nums:
                for slot in slots[num]:
                    if slot not in self._people_to_slots[person]:
                        print(f'removed {slot} from {person}')

    def can_fill(self, conditions=None):
        if conditions is None:
            conditions = []

        num_of_slots = len(list(filter(lambda i: i, self._slots_to_people.values())))

        roaster = self.copy()
        num_filled = 0
        assigned: dict[Slot, Person] = dict()
        while roaster.has_remaining_slots():
            best_slots = roaster.get_best_slots()
            slot, people = next(iter(best_slots.items()))
            person = next(iter(people))

            assigned[slot] = person

            roaster.remove_slot(slot)
            roaster.filter_slots_from_people(lambda s: s.cycle is not slot.cycle, person)

            # clear slot-people combinations that don't meet the requirements
            '''
            to_remove = set()
            for s1 in roaster._slots_to_people:
                if len(roaster._slots_to_people[s1]) == 0:
                    continue
                for p1 in roaster._slots_to_people[s1]:
                    for s2, p2 in assigned.items():
                        if p1 is not p2:
                            continue
                        for condition in conditions:
                            if not condition(s1, s1):
                                to_remove.add((s1, p1))
            for s, p in to_remove:
                roaster._slots_to_people[s].remove(p)
                roaster._people_to_slots[p].remove(s)
            '''

            num_filled += 1

        return num_of_slots == num_filled

    def can_fill2(self, cycle=None, ignore_empty_slots=False):
        slots_to_people: dict[Slot, set[Person]] = dict()
        people_to_slots: dict[Person, set[Slot]] = dict()

        if cycle is None:
            for slot, people in self._slots_to_people.items():
                if len(people) == 0:
                    if ignore_empty_slots:
                        continue
                    return False
                slots_to_people[slot] = people.copy()
            for person, slots in self._people_to_slots.items():
                people_to_slots[person] = slots.copy()
        else:
            for slot in self._cycles[cycle]:
                if len(self._slots_to_people[slot]) == 0:
                    if ignore_empty_slots:
                        continue
                    return False
                slots_to_people[slot] = self._slots_to_people[slot].copy()
                for person in self._slots_to_people[slot]:
                    if person in people_to_slots:
                        people_to_slots[person].add(slot)
                    else:
                        people_to_slots[person] = {slot}

        while slots_to_people:
            # find slot with least people
            slot: Slot = None
            min_num = float('inf')
            for s, people in slots_to_people.items():
                if len(people) < min_num:
                    slot = s
                    if len(people) == 0:
                        return False
                    if len(people) == 1:
                        break
                    min_num = len(people)

            # find person with least slots
            person: Person = None
            min_num = float('inf')
            for p in slots_to_people[slot]:
                num = len(people_to_slots[p])
                if num < min_num:
                    person = p
                    if num == 1:
                        break
                    min_num = num

            # remove person
            for s in people_to_slots[person]:
                if s.cycle is slot.cycle:
                    slots_to_people[s].remove(person)

            # remove that slot
            for p in slots_to_people[slot]:
                people_to_slots[p].remove(slot)
            slots_to_people.pop(slot)

        return True


def slots_to_table(slots_and_people: dict[Slot, set[Person]]):
    people = set()
    slots = list(slots_and_people.keys())

    for p in slots_and_people.values():
        people.update(p)

    people = list(people)

    table = [[''] + [person.get_name() for person in people]]
    for slot in slots:
        row = [repr(slot)] + [''] * len(people)
        table.append(row)
        for person in slots_and_people[slot]:
            row[people.index(person) + 1] = 'x'

    return table