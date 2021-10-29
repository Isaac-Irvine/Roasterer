
class Person:
    def __init__(self, name, jobs, jobs_in_training):
        self._name = name
        self._jobs = jobs
        self._jobs_training = jobs_in_training

    def get_jobs(self):
        return self._jobs

    def is_in_training(self, job):
        return job in self._jobs_training

    def get_name(self):
        return self._name

    def __str__(self):
        return self._name
