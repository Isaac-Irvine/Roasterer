

class Job:
    def __init__(self, name, hard, supervisor=False):
        """
        :param name: name of the job. e.g. "cell 4"
        :param hard: Whether or not the job is considered hard
        """
        self._name = name
        self._hard = hard
        if supervisor is False:
            self._supervisor_job = Job(self._name + ' supervisor', self._hard, supervisor=True)
        else:
            self._supervisor_job = None

    def is_hard(self):
        return self._hard

    def get_supervisor_job(self):
        return self._supervisor_job

    def get_name(self):
        return self._name
