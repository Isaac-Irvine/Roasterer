from job import Job


class Person:
    def __init__(self, name, all_jobs=None, jobs_needing_supervision=None):
        self._all_jobs = [] if all_jobs is None else all_jobs
        self._jobs_needing_supervision = [] if jobs_needing_supervision is None else jobs_needing_supervision
        self._name = name

    def can_do_job(self, job: Job) -> bool:
        return job in self._all_jobs

    def get_all_jobs(self):
        return self._all_jobs

    def add_job(self, job, supervision_needed=False):
        self._all_jobs.append(job)
        if supervision_needed:
            self._jobs_needing_supervision.append(job)

    def needs_supervision(self, job):
        return job in self._jobs_needing_supervision

    def get_name(self):
        return self._name

    def __str__(self):
        return self._name
