from person import Person


class Cycle:
    def __init__(self, name: str, jobs_needed=None, people_available=None, jobs_assigned=None):
        self._name = name
        self._jobs = [] if jobs_needed is None else jobs_needed
        self._people = [] if people_available is None else people_available
        # maps people to job
        self._assigned = {} if jobs_assigned is None else jobs_assigned

    def get_spare_people(self) -> Person:
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

    def get_persons_job(self, person):
        return self._assigned[person]

    def get_name(self):
        return self._name

    def is_assigned(self, person):
        return person in self._assigned

    def __str__(self):
        return self._name
