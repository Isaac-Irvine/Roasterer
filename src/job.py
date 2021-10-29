

class Job:

    def __init__(self, name, hard):
        """
        :param name: name of the job. e.g. "cell 4"
        :param hard: Whether or not the job is considered hard
        """
        self._name = name
        self._hard = hard

    def is_hard(self):
        return self._hard

    def get_training_job(self):
        pass

    def get_name(self):
        return self._name
