

class Cycle:
    def __init__(self, name, jobs_needed, people_available, jobs_assigned=dict()):
        self._name = name
        self._jobs = jobs_needed
        self._people = people_available
        self._assigned = jobs_assigned  # maps people to job

    def get_spare_people(self):
        return self._people

    def get_spare_jobs(self):
        return self._jobs

    def get_all_jobs(self):
        return self._jobs + list(self._assigned.values())

    def assign(self, job, person):
        self._assigned[person] = job
        self._people.remove(person)
        self._jobs.remove(job)

    def add_job(self, job):
        self._jobs.append(job)

    def add_person(self, person):
        self._people.append(person)

    def copy(self):
        return Cycle(self._name, self._jobs.copy(), self._people.copy(), self._assigned.copy())

    def get_assigned(self):
        return self._assigned

    def get_job_assignee(self, job):
        pass  # TODO

    def get_persons_job(self, person):
        return self._assigned[person]

    def get_name(self):
        return self._name

    def is_assigned(self, person):
        return person in self._assigned

    def __str__(self):
        return self._name

    #def __repr__(self):  # temp
    #    return f"{self._name}. \n" \
    #           f"Assigned jobs: {self._assigned} \n" \
    #           f"Spare jobs: {self._jobs} \n" \
    #           f"Spare people: {self._people}"

    # def is_filled(self):
    #    return len(self._people) == 0 or len(self._jobs) == 0
