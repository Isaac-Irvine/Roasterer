from functools import cmp_to_key
from random import choice

from roaster import Roaster


# (mostly) randomised recursive depth first search for valid timetables
# Will take a huge amount of time to go through all possibilities
def _fill_cycle(cycle, last_cycle=None):
    if len(cycle.get_spare_jobs()) == 0:
        yield cycle
        return

    if len(cycle.get_spare_people()) == 0:
        return

    person = choice(cycle.get_spare_people())

    # priorities:
    # don't do the same hard job twice in a row
    # don't have as few hard jobs per day per person. todo: implement this
    # don't do the same job twice in a row jobs
    # don't do the same job twice in a day. todo: implement this
    def compare(job_1, job_2):
        # if the second is better, return 1
        # return -1 if the first is better and 0 if they are the same
        if last_cycle is None or not last_cycle.is_assigned(person):
            return 0

        last_job = last_cycle.get_persons_job(person)

        # don't do the same hard job twice in a row
        if last_job.is_hard():
            if not job_1.is_hard() and job_2.is_hard():
                return -1
            if job_1.is_hard() and not job_2.is_hard():
                return 1

        # don't do the same job twice in a row jobs
        if last_job is job_1 and last_job is not job_2:
            return 1
        if last_job is job_2 and last_job is not job_1:
            return -1
        return 0

    jobs = filter(lambda j: j in person.get_all_jobs(), cycle.get_spare_jobs())
    if last_cycle is not None and last_cycle.is_assigned(person) and last_cycle.get_persons_job(person).is_hard():
        jobs = filter(lambda j: not j.is_hard(), jobs)
    jobs = list(jobs)
#    jobs.sort(key=cmp_to_key(compare))

    for job in jobs:
        new_cycle = cycle.copy()
        new_cycle.assign(job, person)

        if person.needs_supervision(job):
            new_cycle.add_job(job.get_supervisor_job())

        yield from _fill_cycle(new_cycle, last_cycle)


def _find_roaster(cycles, filled_cycles):
    if not cycles:
        yield filled_cycles
        return

    for cycle_attempt in _fill_cycle(cycles[0], filled_cycles[-1] if filled_cycles else None):
        yield from _find_roaster(cycles[1:], filled_cycles + [cycle_attempt])


def find_roaster(roaster):
    return Roaster(next(_find_roaster(roaster.get_cycles(), [])))
