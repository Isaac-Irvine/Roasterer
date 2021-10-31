

class Job:

    def __init__(self, name, hard, is_trainer=False):
        """
        :param name: name of the job. e.g. "cell 4"
        :param hard: Whether or not the job is considered hard
        """
        self._name = name
        self._hard = hard
        if is_trainer is False:
            self._trainer_job = Job(self._name + " trainer", self._hard, is_trainer=True)

    def is_hard(self):
        return self._hard

    def get_trainer_job(self):
        return self._trainer_job

    def get_name(self):
        return self._name
