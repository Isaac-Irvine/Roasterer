from roster7 import Cycle
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
    cycles: list[Cycle] = [Cycle(i) for i in range(1, 5)]

    jobs: dict[str, ] = {}  # maps names of jobs to jobs
    job_groups = {}  # maps names of job groups to job groups
    people = {}  # maps peoples names to people
    roaster = Roster()
    roaster.cycles = cycles

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
        roaster.jobs.append(job)

        for i in range(0, 4):
            if to_bool(row[i + 4]):
                cycles[i].jobs.append(job)

    # parse people and jobs table
    jobs_list = [jobs[j] for j in people_jobs[0][1:]]

    for row in filter(lambda r: r[0] != '', people_jobs[1:]):
        name = row[0]
        person = Person(name)
        people[name] = person
        roaster.people.append(person)

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
                cycle.fully_available_people.append(person)
            elif cell == 'Casual only':
                cycle.casually_available_people.append(person)

    # parsing roaster hard coding
    for cycle, row in zip(cycles, filter(lambda r: r[0] != '', roster_hard_coding[1:])):
        for job, cell in zip(jobs_list, row[1:]):
            if cell != '':
                if cell not in people:
                    raise RuntimeError(
                        f'nobody called {cell} found in the Roaster hard coding sheet. '
                        f'If this isn\'t a typo, make sure the person is in the People and Job sheet'
                    )
                roaster.assign(cycle, job, people[cell])

    return roaster
