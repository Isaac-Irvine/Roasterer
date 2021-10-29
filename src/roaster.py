

class Roaster:

    def __init__(self, cycles):
        self._cycles = cycles

    def get_cycles(self):
        return self._cycles

    def copy(self):
        return Roaster(self._cycles.copy())

    def to_table(self):
        all_jobs_set = set()
        for cycle in self._cycles:
            all_jobs_set = all_jobs_set.union(set(cycle.get_all_jobs()))

        all_jobs_ordered = list(all_jobs_set)

        table = [[None] + [job.get_name() for job in all_jobs_ordered]]
        for cycle in self._cycles:
            row = [None] * len(all_jobs_ordered)
            for person, job in cycle.get_assigned().items():
                row[all_jobs_ordered.index(job)] = person.get_name()
            table.append([cycle.get_name()] + row)
        return table
