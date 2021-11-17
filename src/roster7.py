from time import time
from random import choice

from tabulate import tabulate

from cycle import Cycle
from job import Job
from person import Person
from slot import Slot, PotentialSlots


# scored. Find the best score


class Roster:

    def __init__(self):
        self._slots: PotentialSlots = PotentialSlots()
        self._assigned_slots: dict[Slot, Person] = dict()
        self._assigned_people: dict[Person, set[Slot]] = dict()
        self._cycles: list[Cycle] = []
        self._jobs_order: list[Job] = []
        self._people = set()


    def add_person(self, person: Person):
        self._people.add(person)

    def add_cycle(self, cycle: Cycle):
        """

        """
        self._cycles.append(cycle)
        self._slots = self._slots.union(cycle.get_potential_slots())

        if not cycle.get_potential_slots().can_fill():
            print(f'Can\'t fill all of {cycle}\'s slots')

    def get_cycles(self) -> list[Cycle]:
        return self._cycles

    def get_jobs(self) -> list[Job]:
        return self._jobs_order

    def set_jobs_order(self, jobs_order: list[Job]):
        """
        Sets the display order of the jobs when converting the roaster to a table.
        Has no purpose other than improving readability of the table
        """
        self._jobs_order = jobs_order

    def _generate_potential(self):
        for cycle in self._cycles:
            for job in cycle.get_jobs():
                for person in cycle.get_available():
                    self._slots.add_potential_person()

    def assign(self, person: Person, slot: Slot):
        """
        Assigns the given slot to the given person.
        """

        self._assigned_slots[slot] = person
        if person in self._assigned_people:
            self._assigned_people[person].add(slot)
        else:
            self._assigned_people[person] = {slot}

        # don't assign other people the slot
        self._slots.remove_slot(slot)

        # don't assign this person other slots in the same cycle
        self._slots.filter_slots_from_people(lambda s: s.cycle is not slot.cycle, person)

    def unassign(self, slot: Slot):
        self._assigned_slots.pop(slot)

    def get_slots(self) -> set[Slot]:
        return self._slots.get_slots()

    def score(self):
        """
        calculates a score
        """
        conditions = [
                # same hard job in cycle 2 and 3
                lambda s1, s2:
                s1.job is s2.job
                and s1.job.is_hard()
                and s1.cycle in {self._cycles[1], self._cycles[2]}
                and s2.cycle in {self._cycles[1], self._cycles[2]},

                # two hard jobs in the same line in cycle 2 and 3
                lambda s1, s2:
                s1.job.get_job_group() is not None
                and s1.job.get_job_group() is s2.job.get_job_group()
                and s1.job.is_hard() and s2.job.is_hard()
                and s1.cycle in {self._cycles[1], self._cycles[2]}
                and s2.cycle in {self._cycles[1], self._cycles[2]},

                # two hard jobs in cycle 2 and 3
                lambda s1, s2:
                s1.job.is_hard() and s2.job.is_hard()
                and s1.cycle in {self._cycles[1], self._cycles[2]}
                and s2.cycle in {self._cycles[1], self._cycles[2]},

                # same hard job consecutively
                lambda s1, s2:
                s1.job is s2.job
                and s1.job.is_hard()
                and s1.cycle.next_to(s2.cycle),

                # two hard jobs in the same line consecutively
                lambda s1, s2:
                s1.job.get_job_group() is not None
                and s1.job.get_job_group() is s2.job.get_job_group()
                and s1.job.is_hard() and s2.job.is_hard()
                and s1.cycle.next_to(s2.cycle),

                # two hard jobs consecutively
                lambda s1, s2:
                s1.job.is_hard() and s2.job.is_hard()
                and s1.cycle.next_to(s2.cycle),

                # same job in cycle 2 and 3
                lambda s1, s2:
                s1.job is s2.job
                and s1.cycle in {self._cycles[1], self._cycles[2]}
                and s2.cycle in {self._cycles[1], self._cycles[2]},

                # two jobs in the same line in cycle 2 and 3
                lambda s1, s2:
                s1.job.get_job_group() is not None
                and s1.job.get_job_group() is s2.job.get_job_group()
                and s1.cycle in {self._cycles[1], self._cycles[2]}
                and s2.cycle in {self._cycles[1], self._cycles[2]},

                # same job consecutively
                lambda s1, s2:
                s1.job is s2.job
                and s1.cycle.next_to(s2.cycle),

                # two jobs in the same line consecutively
                lambda s1, s2:
                s1.job.get_job_group() is not None
                and s1.job.get_job_group() is s2.job.get_job_group()
                and s1.cycle.next_to(s2.cycle),

                # multiple of the same hard job
                lambda s1, s2:
                s1.job is s2.job
                and s1.job.is_hard(),

                # multiple hard jobs in the same line
                lambda s1, s2:
                s1.job.get_job_group() is not None
                and s1.job.get_job_group() is s2.job.get_job_group()
                and s1.job.is_hard() and s2.job.is_hard(),

                # multiple hard jobs
                lambda s1, s2:
                s1.job.is_hard() and s2.job.is_hard(),

                # multiple of the same job
                lambda s1, s2:
                s1.job is s2.job,

                # multiple jobs on the same line
                lambda s1, s2:
                s1.job.get_job_group() is not None
                and s1.job.get_job_group() is s2.job.get_job_group(),
            ]

        scores = [0] * len(conditions)
        for person in self._assigned_people:
            slots = list(self._assigned_people[person])
            for i, condition in enumerate(conditions):
                for j in range(0, len(slots)):
                    for k in range(j+1, len(slots)):
                        if condition(slots[j], slots[k]):
                            scores[i] += 1
        return [len(set(self._slots.get_slots().difference(self._assigned_slots.keys())))] + scores

    @staticmethod
    def _better_than(scores_1, scores_2):
        for score_1, score_2 in zip(scores_1, scores_2):
            if score_1 < score_2:
                return True
            elif score_1 > score_2:
                return False
        return True  # doesn't matter, they are the same

    def fill(self):
        best = None
        best_scores = []
        for i in range(0, 10000):
            slots = self._slots.copy()
            self._assigned_slots.clear()
            self._assigned_people.clear()
            self._fill()
            score = self.score()
            if self._better_than(score, best_scores):
                best = self._assigned_slots.copy()
                best_scores = score
            self._slots = slots
        self._assigned_slots = best

    def _fill(self):
        while self._slots.has_remaining_slots():
            slot, person = self._slots.get_random_assignable()

            # if the jobs needs a supervisor, make a supervisor job
            # but if nobody can do the supervisor role, remove the role from the person
            '''
            if person.needs_supervision(slot.job):
                if not slot.cycle.add_job(slot.job.get_supervisor_job()):
                    self._possible_slots[person].remove(slot)
                    continue
            '''
            self.assign(person, slot)

    def _has_job(self, person: Person, cycle=None) -> bool:
        for slot, p in self._assigned_slots.items():
            if p is person:
                if cycle is not None and slot.cycle is not cycle:
                    continue
                return True
        return False

    def get_available(self, cycle: Cycle) -> set[Person]:
        people = set()
        for person in cycle.get_available():
            if not self._has_job(person, cycle):
                people.add(person)
        return people

    def get_casually_available(self, cycle: Cycle) -> set[Person]:
        people = set()
        for person in cycle.get_casually_available():
            if not self._has_job(person, cycle):
                people.add(person)
        return people

    def get_slot(self, job: Job, cycle: 'Cycle') -> Slot:
        return self._slots.get_slot(job, cycle)

    def get_assigned(self) -> dict[Slot, Person]:
        return self._assigned_slots

    def to_table(self) -> list[list[str]]:
        # add all the jobs that aren't already in jobs_order into it
        # probably just supervisors
        for slot in filter(lambda s: s.job not in self._jobs_order, self._assigned_slots.keys()):
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

        # make table
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
        for slot, person in self._assigned_slots.items():
            table[self._cycles.index(slot.cycle) + 1][self._jobs_order.index(slot.job) + 1] = person.get_name()

        return table

    def to_table_people(self) -> list[list[str]]:
        # add all the jobs that aren't already in jobs_order into it
        # probably just supervisors

        people = list(self._slots.get_people())

        # make table
        table = []
        table.append([''] + [person.get_name() for person in people]
                     )
        for i, cycle in enumerate(self._cycles):
            table.append([cycle.get_name()] + [''] * len(people))

        # make a table of all the cycles and jobs
        for slot, person in self._assigned_slots.items():
            table[self._cycles.index(slot.cycle) + 1][people.index(person) + 1] = slot.job.get_name()

        return table
