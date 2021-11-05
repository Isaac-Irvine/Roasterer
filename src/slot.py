from job import Job


class Slot:
    def __init__(self, cycle, job: Job, available_for_training: bool):
        self.job = job
        self.cycle = cycle
        self.available_for_training = available_for_training

    def __repr__(self):
        return f'{self.cycle.get_name()} {self.job.get_name()}'
