class JobGroup:
    def __init__(self, name: str):
        self._name = name

    def get_name(self) -> str:
        return self._name


class Job:
    def __init__(self, name: str, job_group: JobGroup, hard: bool, casual: bool, supervisor: bool = False):
        """
        :param name: name of the job. e.g. "cell 4"
        :param hard: Whether or not the job is considered hard
        """
        self._name = name
        self._job_group = job_group
        self._hard = hard
        self._casual = casual
        if supervisor is False:
            self._supervisor_job = Job(self._name + ' supervisor', self._job_group, self._hard, casual, supervisor=True)
        else:
            self._supervisor_job = None

    def set_name(self, name: str):
        self._name = name

    def set_hard(self, hard: bool):
        self._hard = hard

    def is_hard(self) -> bool:
        return self._hard

    def set_casual(self, casual: bool):
        self._casual = casual

    def is_casual(self) -> bool:
        return self._casual

    def get_supervisor_job(self) -> 'Job':
        return self._supervisor_job

    def get_name(self) -> str:
        return self._name

    def get_job_group(self) -> JobGroup:
        return self._job_group

    def __repr__(self) -> str:
        return self._name
