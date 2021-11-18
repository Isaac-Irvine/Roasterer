from random import choice

from tabulate import tabulate
from job import Job
from person import Person
from scipy.optimize import linear_sum_assignment
import numpy as np


# scored. Find the best score

class Cycle:
    def __init__(self, number):
        self.jobs: list[Job] = []
        self.fully_available_people: list[Person] = []
        self.casually_available_people: list[Person] = []
        self.number: int = number

    def get_name(self) -> str:
        return f'Cycle {self.number}'

    def __repr__(self) -> str:
        return f'Cycle({self.number})'

    def next_to(self, cycle: 'Cycle'):
        return abs(cycle.number - self.number) == 1


class Roster:
    def __init__(self):
        self.jobs: list[Job] = []
        self.people: list[Person] = []
        self.cycles: list[Cycle] = []
        self.assigned: dict[Cycle, dict[Person, Job]] = {}

    def copy(self):
        new = Roster()
        new.jobs = self.jobs.copy()
        new.people = self.people.copy()
        new.cycles = self.cycles.copy()
        for cycle in self.assigned:
            new.assigned[cycle] = dict()
            for person, job in self.assigned[cycle].items():
                new.assigned[cycle][person] = job
        return new

    def assign(self, cycle: Cycle, job: Job, person: Person):
        if cycle not in self.assigned:
            self.assigned[cycle] = {}
        self.assigned[cycle][person] = job

    def fill(self):
        for cycle in self.cycles:
            if cycle not in self.assigned:
                self.assigned[cycle] = dict()

        for i in range(1):
            for cycle in self.cycles:
                costs = self.get_cost_matrix(cycle)
                row_ind, col_ind = linear_sum_assignment(costs)
                for job_index, person_index in zip(row_ind, col_ind):
                    self.assigned[cycle][cycle.fully_available_people[person_index]] = cycle.jobs[job_index]

    def get_cost_matrix(self, cycle: Cycle) -> np.ndarray:
        # jobs is row
        # people are col
        # TODO: Randomise job or people order
        matrix = np.full((len(cycle.jobs), len(cycle.fully_available_people)), 999999999999)
        for row, job in enumerate(cycle.jobs):
            for col, person in enumerate(cycle.fully_available_people):
                if person.can_do_job(job):
                    matrix[row][col] = 0

        return matrix

    def assigned_to_table(self):
        table = [[''] + [job.get_name() for job in self.jobs]]
        for cycle in self.cycles:
            row = [cycle.get_name()] + [''] * len(self.jobs)
            if cycle not in self.assigned:
                continue
            for person, job in self.assigned[cycle].items():
                row[self.jobs.index(job) + 1] = person.get_name()
            table.append(row)
        return table

    @staticmethod
    def costs_to_table(costs, jobs, people):
        table = [[''] + [job.get_name() for job in jobs]]
        for person in people:
            pass

    def print_table(self):
        print(tabulate(self.assigned_to_table(), headers='firstrow'))
