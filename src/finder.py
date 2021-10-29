from random import choice

from roaster import Roaster


# (mostly) randomised recursive depth first search for valid timetables
def _fill_cycle(cycle, last_cycle=None):
    if len(cycle.get_spare_jobs()) == 0:
        yield cycle
        return

    if len(cycle.get_spare_people()) == 0:
        return

    person = choice(cycle.get_spare_people())

    last_job_hard = last_cycle is not None and last_cycle.is_assigned(person) and last_cycle.get_persons_job(person).is_hard()

    for skip_hards in (True, False) if last_job_hard else (False, ):
        for job in cycle.get_spare_jobs():
            if job not in person.get_jobs() or skip_hards and job.is_hard():
                continue

            new_cycle = cycle.copy()
            new_cycle.assign(job, person)

            if person.is_in_training(job):
                new_cycle.add_job(job.get_training_job())

            yield from _fill_cycle(new_cycle, last_cycle)


def _find_roaster(cycles, filled_cycles):
    if not cycles:
        yield filled_cycles

    for cycle_attempt in _fill_cycle(cycles[0], filled_cycles[-1] if filled_cycles else None):
        yield from _find_roaster(cycles[1:], filled_cycles + [cycle_attempt])


def find_roaster(roaster):
    return Roaster(next(_find_roaster(roaster.get_cycles(), [])))
