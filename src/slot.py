#from cycle2 import Cycle
from job import Job


class Slot:
    def __init__(self, cycle, job: Job, available_for_training: bool):
        self.job = job
        self.cycle = cycle
        self.available_for_training = available_for_training
