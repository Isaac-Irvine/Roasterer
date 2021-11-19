from random import choice, shuffle

from tabulate import tabulate
from job import Job
from person import Person
from scipy.optimize import linear_sum_assignment
import numpy as np

# TODO: get scoring right
CANT_DO_SCORE = 1000
FILL_CONDITIONS = (
    # same hard job in cycle 2 and 3
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job is potential_job
        and assigned_job.is_hard()
        and assigned_cycle.is_long() and potential_cycle.is_long(),
        35
    ),

    # two hard jobs in the same line in cycle 2 and 3
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.get_job_group() is not None
        and assigned_job.get_job_group() is potential_job.get_job_group()
        and assigned_job.is_hard() and potential_job.is_hard()
        and assigned_cycle.is_long() and potential_cycle.is_long(),
        34
    ),

    # two hard jobs in cycle 2 and 3
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.is_hard() and potential_job.is_hard()
        and assigned_cycle.is_long() and potential_cycle.is_long(),
        33
    ),

    # same hard job consecutively
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job is potential_job
        and assigned_job.is_hard()
        and assigned_cycle.next_to(potential_cycle),
        32
    ),

    # two hard jobs in the same line consecutively
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.get_job_group() is not None
        and assigned_job.get_job_group() is potential_job.get_job_group()
        and assigned_job.is_hard() and potential_job.is_hard()
        and assigned_cycle.next_to(potential_cycle),
        31
    ),

    # two hard jobs consecutively
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.is_hard() and potential_job.is_hard()
        and assigned_cycle.next_to(potential_cycle),
        30
    ),

    # same job in cycle 2 and 3
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job is potential_job
        and assigned_cycle.is_long() and potential_cycle.is_long(),
        23
    ),

    # two jobs in the same line in cycle 2 and 3
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.get_job_group() is not None
        and assigned_job.get_job_group() is potential_job.get_job_group()
        and assigned_cycle.is_long()
        and potential_cycle.is_long(),
        22
    ),

    # same job consecutively
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job is potential_job
        and assigned_cycle.next_to(potential_cycle),
        21
    ),

    # two jobs in the same line consecutively
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.get_job_group() is not None
        and assigned_job.get_job_group() is potential_job.get_job_group()
        and assigned_cycle.next_to(potential_cycle),
        20
    ),

    # multiple of the same hard job
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job is potential_job
        and assigned_job.is_hard(),
        14
    ),

    # multiple hard jobs in the same line
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.get_job_group() is not None
        and assigned_job.get_job_group() is potential_job.get_job_group()
        and assigned_job.is_hard() and potential_job.is_hard(),
        13
    ),

    # multiple hard jobs
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.is_hard() and potential_job.is_hard(),
        12
    ),

    # multiple of the same job
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job is potential_job,
        11
    ),

    # multiple jobs on the same line
    (
        lambda assigned_job, assigned_cycle, potential_job, potential_cycle:
        assigned_job.get_job_group() is not None
        and assigned_job.get_job_group() is potential_job.get_job_group(),
        10
    )
)


class Cycle:
    def __init__(self, number):
        self.jobs: set[Job] = set()
        self.fully_available_people: set[Person] = set()
        self.casually_available_people: set[Person] = set()
        self.number: int = number

    def copy(self):
        new = Cycle(self.number)
        new.jobs = self.jobs.copy()
        new.fully_available_people = self.fully_available_people.copy()
        new.casually_available_people = self.casually_available_people.copy()
        return new

    def get_name(self) -> str:
        return f'Cycle {self.number}'

    def __repr__(self) -> str:
        return f'Cycle({self.number})'

    def next_to(self, cycle: 'Cycle'):
        return abs(cycle.number - self.number) == 1

    def is_long(self):
        return self.number == 2 or self.number == 3

    def set_casual(self, person: Person, casual: bool):
        if casual and person in self.fully_available_people:
            self.fully_available_people.remove(person)
            self.casually_available_people.add(person)
        if not casual and person in self.casually_available_people:
            self.casually_available_people.remove(person)
            self.fully_available_people.add(person)

    def remove_person(self, person: Person):
        if person in self.fully_available_people:
            self.fully_available_people.remove(person)
        if person in self.casually_available_people:
            self.casually_available_people.remove(person)

    def can_fill(self):
        pass


class Roster:
    def __init__(self):
        self.jobs: list[Job] = []  # switch to Set()?
        self.people: set[Person] = set()
        self.cycles: list[Cycle] = []
        self.assigned: dict[Cycle, dict[Person, Job]] = {}

    def copy(self):
        new = Roster()
        new.jobs = self.jobs.copy()
        new.people = self.people.copy()
        new.cycles = self.cycles.copy()
        new.assigned = self._get_assigned_copy()
        return new

    def deep_copy(self):
        new = Roster()
        new.jobs = self.jobs.copy()
        new.people = self.people.copy()
        for cycle in self.cycles:
            new_cycle = cycle.copy()
            new.cycles.append(new_cycle)
            if cycle in self.assigned:
                new.assigned[new_cycle] = dict()
                for person, job in self.assigned[cycle].items():
                    new.assigned[new_cycle][person] = job
        return new

    def _get_assigned_copy(self) -> dict[Cycle, dict[Person, Job]]:
        new = dict()
        for cycle in self.assigned:
            new[cycle] = dict()
            for person, job in self.assigned[cycle].items():
                new[cycle][person] = job
        return new

    def assign(self, cycle: Cycle, job: Job, person: Person):
        if cycle not in self.assigned:
            self.assigned[cycle] = {}
        self.assigned[cycle][person] = job

    def unassign(self, cycle: Cycle, person: Person):
        self.assigned[cycle].pop(person)

    def get_assinged_person(self, cycle: Cycle, job: Job):
        if cycle in self.assigned:
            for person, j in self.assigned[cycle].items():
                if j is job:
                    return person

    def get_unassinged_fully_available(self, cycle: Cycle):
        if cycle not in self.assigned:
            return cycle.fully_available_people
        people = set()
        for person in cycle.fully_available_people:
            if person not in self.assigned[cycle]:
                people.add(person)
        return people

    def get_unassinged_casually_available(self, cycle: Cycle):
        if cycle not in self.assigned:
            return cycle.casually_available_people
        people = set()
        for person in cycle.casually_available_people:
            if person not in self.assigned[cycle]:
                people.add(person)
        return people

    def get_unassinged_available(self, cycle):
        return self.get_unassinged_casually_available(cycle).union(self.get_unassinged_fully_available(cycle))

    def get_unavailable(self, cycle: Cycle):
        return self.people.difference(cycle.casually_available_people.union(cycle.fully_available_people))

    def get_unassinged_jobs(self, cycle: Cycle) -> set[Job]:
        if cycle not in self.assigned:
            return set(cycle.jobs)
        jobs = set()
        for job in cycle.jobs:
            if job not in self.assigned[cycle].values():
                jobs.add(job)
        return jobs

    def fill(self):
        for cycle in self.cycles:
            if cycle not in self.assigned:
                self.assigned[cycle] = dict()

        min_score = float('inf')
        min_assigned: dict[Cycle, dict[Person, Job]] = None

        for i in range(100):
            start = self._get_assigned_copy()
            score = 0
            for cycle in self.cycles:
                costs, people, jobs = self._get_cost_matrix(cycle)
                row_ind, col_ind = linear_sum_assignment(costs)
                score += costs[row_ind, col_ind].sum()
                for job_index, person_index in zip(row_ind, col_ind):
                    if costs[job_index][person_index] < CANT_DO_SCORE:
                        self.assigned[cycle][people[person_index]] = jobs[job_index]
            if score < min_score:
                min_assigned = self.assigned
                min_score = score
            self.assigned = start
        self.assigned = min_assigned

    def _get_cost_matrix(self, cycle: Cycle) -> tuple[np.ndarray, list[Person], list[Job]]:
        # jobs is row
        # people are col
        people = list(self.get_unassinged_available(cycle))
        jobs = list(self.get_unassinged_jobs(cycle))
        shuffle(people)
        matrix = np.full((len(jobs), len(people)), 999999999999)
        for row, job in enumerate(jobs):
            for col, person in enumerate(people):
                matrix[row][col] = self._get_score(cycle, job, person)

        return matrix, people, jobs

    def _get_score(self, cycle: Cycle, job: Job, person: Person) -> int:
        if not person.can_do_job(job):
            return CANT_DO_SCORE
        if person in cycle.casually_available_people and not job.is_casual():
            return CANT_DO_SCORE
        for condition, score in FILL_CONDITIONS:
            num = 0
            for c in self.assigned:
                if (
                    c is not cycle
                    and person in self.assigned[c]
                    and condition(job, cycle, self.assigned[c][person], c)
                ):
                    num += 1
            if num != 0:
                return num * score
        return 0
