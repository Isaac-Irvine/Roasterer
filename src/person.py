from job import Job


class Person:
    def __init__(self, name):
        self._all_jobs = []
        self._name = name

    def can_do_job(self, job: Job) -> bool:
        return job in self._all_jobs

    def get_jobs(self):
        return self._all_jobs

    def add_job(self, job):
        self._all_jobs.append(job)

    def remove_job(self, job):
        self._all_jobs.remove(job)

    def get_name(self):
        return self._name

    def set_name(self, name: str):
        self._name = name

    def __repr__(self):
        return self._name
