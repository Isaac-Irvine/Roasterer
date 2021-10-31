

class Person:
    def __init__(self, name, all_jobs=None, jobs_in_training=None):
        self._all_jobs = [] if all_jobs is None else all_jobs
        self._jobs_training = [] if jobs_in_training is None else jobs_in_training
        self._name = name

    def get_all_jobs(self):
        return self._all_jobs

    def add_job(self, job, trainee=False):
        self._all_jobs.append(job)
        if trainee:
            self._jobs_training.append(job)

    def is_in_training(self, job):
        return job in self._jobs_training

    def get_name(self):
        return self._name

    def __str__(self):
        return self._name
