from cycle import Cycle
from job import Job
from person import Person
from roaster import Roaster


def to_bool(string):
    if string == 'TRUE':
        return True
    elif string == 'FALSE':
        return False
    raise RuntimeError(f'Cell is not TRUE or FALSE. Got "{string}"')


def parse_table(jobs_cycles, people_availability, people_jobs, roaster_hard_coding):
    cycles = [Cycle(f'Cycle {i}') for i in range(1, 5)]

    jobs = {}
    people = {}

    # parsing jobs and cycles table
    for row in filter(lambda r: r[0] != '', jobs_cycles[1:]):
        job = Job(row[0], to_bool(row[1]))
        jobs[row[0]] = job

        for i in range(0, 4):
            if to_bool(row[i + 2]):
                cycles[i].add_job(job)

    # parsing people and availability table
    for row in filter(lambda r: r[0] != '', people_availability[1:]):
        name = row[0]
        person = Person(name)
        people[name] = person

        for cycle, cell in zip(cycles, row[1:5]):
            if to_bool(cell):
                cycle.add_person(person)

    # parse people and jobs table
    jobs_list = [jobs[j] for j in people_jobs[0][1:]]

    for row in filter(lambda r: r[0] != '', people_jobs[1:]):
        if row[0] not in people:
            raise RuntimeError(
                f'There is a person called "{row[0]}" in the People and Jobs sheet thats not in the People and Availability sheet'
            )
        person = people[row[0]]
        for i, cell in enumerate(row[1:]):
            if cell == '':
                continue
            job = jobs_list[i]
            person.add_job(job, cell == 'Supervised trainee')
            if cell == 'Trainer':
                person.add_job(job.get_supervisor_job())

    # parsing roaster hard coding
    for cycle, row in zip(cycles, filter(lambda r: r[0] != '', roaster_hard_coding[1:])):
        for job, cell in zip(jobs_list, row[1:]):
            if cell != '':
                cycle.assign(job, people[cell])  # TODO: validate this

    return Roaster(cycles, jobs_list)
