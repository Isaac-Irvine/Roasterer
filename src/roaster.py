

class Roaster:

    def __init__(self, cycles):
        self._cycles = cycles

    def get_cycles(self):
        return self._cycles

    def copy(self):
        return Roaster(self._cycles.copy())

    def to_table(self, jobs_order=None):
        if jobs_order is None:
            jobs_order = []

        # get all jobs
        all_jobs_set = set()
        for cycle in self._cycles:
            all_jobs_set = all_jobs_set.union(set(cycle.get_all_jobs()))

        # add all the jobs that aren't already in jobs_order into it
        for job in filter(lambda j: j not in jobs_order, all_jobs_set):
            for i in range(0, len(jobs_order)):
                if job.get_name().startswith(jobs_order[i].get_name()):
                    jobs_order.insert(i + 1, job)
                    break
            else:
                jobs_order.append(job)

        # make a table of all the cycles and jobs
        table = [[None] + [job.get_name() for job in jobs_order]]
        for cycle in self._cycles:
            row = [cycle.get_name()] + [None] * len(jobs_order)
            for person, job in cycle.get_assigned().items():
                row[jobs_order.index(job) + 1] = person.get_name()
            table.append(row)

        return table
