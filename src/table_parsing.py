from cycle import Cycle
from job import Job, JobGroup
from person import Person
from roster7 import Roster


def to_bool(string):
    if string == 'TRUE':
        return True
    elif string == 'FALSE':
        return False
    raise RuntimeError(f'Cell is not TRUE or FALSE. Got "{string}"')


def parse_table(jobs_cycles, people_availability, people_jobs, roster_hard_coding):
    cycles = [Cycle(i) for i in range(1, 5)]

    jobs = {}  # maps names of jobs to jobs
    job_groups = {}  # maps names of job groups to job groups
    people = {}  # maps peoples names to people
    roaster = Roster()

    # parsing jobs and cycles table
    for row in filter(lambda r: r[0] != '', jobs_cycles[1:]):
        if row[3] in job_groups:
            job_group = job_groups[row[3]]
        elif row[3] != '':
            job_group = JobGroup(row[3])
            job_groups[row[3]] = job_group
        else:
            job_group = None
        job = Job(row[0], job_group, to_bool(row[1]), to_bool(row[2]))
        jobs[row[0]] = job

        for i in range(0, 4):
            if to_bool(row[i + 4]):
                cycles[i].add_job(job, to_bool(row[i + 7]))

    # parse people and jobs table
    jobs_list = [jobs[j] for j in people_jobs[0][1:]]

    for row in filter(lambda r: r[0] != '', people_jobs[1:]):
        name = row[0]
        person = Person(name)
        people[name] = person
        roaster.add_person(person)

        for i, cell in enumerate(row[1:]):
            if cell == '':
                continue
            job = jobs_list[i]
            person.add_job(job, cell == 'Supervised trainee')
            if cell == 'Trainer':
                person.add_job(job.get_supervisor_job())

    # parsing people and availability table
    for row in filter(lambda r: r[0] != '', people_availability[1:]):
        if row[0] not in people:
            raise RuntimeError(
                f'Nobody called "{row[0]}" found in the People and Availability sheet. '
                f'If this isn\'t a typo, make sure the person is in the People and Jobs sheet'
            )
        person = people[row[0]]

        for cycle, cell in zip(cycles, row[1:5]):
            if cell == 'Available':
                cycle.add_person(person, False)
            elif cell == 'Casual only':
                cycle.add_person(person, True)

    # setting up roaster
    roaster.set_jobs_order(jobs_list)
    for cycle in cycles:
        roaster.add_cycle(cycle)

    # parsing roaster hard coding
    for cycle, row in zip(cycles, filter(lambda r: r[0] != '', roster_hard_coding[1:])):
        for job, cell in zip(jobs_list, row[1:]):
            if cell != '':
                if cell not in people:  # TODO: This doesn't catch people if they are unavailable but still assigned
                    raise RuntimeError(
                        f'nobody called {cell} found in the Roaster hard coding sheet. '
                        f'If this isn\'t a typo, make sure the person is in the People and Job sheet'
                    )
                if cell not in cycle.get_people():
                    cycle.add_person(people[cell], False)
                roaster.assign(people[cell], roaster.get_slot(job, cycle))

    return roaster
