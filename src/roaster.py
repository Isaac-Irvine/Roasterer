

class Roaster:

    def __init__(self, cycles, jobs_display_order=None):
        self._job_order = [] if jobs_display_order is None else jobs_display_order
        self._cycles = cycles
        self._issues = []

    def get_cycles(self):
        return self._cycles

    def get_all_people(self):
        people = set()
        for cycle in self._cycles:
            people = people.union(cycle.get_all_people())
        return people

    def copy(self):
        return Roaster(self._cycles.copy(), jobs_display_order=self._job_order)

    def to_table(self):
        # get all jobs
        all_jobs_set = set()
        for cycle in self._cycles:
            all_jobs_set = all_jobs_set.union(set(cycle.get_all_jobs()))

        # add all the jobs that aren't already in jobs_order into it
        for job in filter(lambda j: j not in self._job_order, all_jobs_set):
            for i in range(0, len(self._job_order)):
                if job.get_name().startswith(self._job_order[i].get_name()):
                    self._job_order.insert(i + 1, job)
                    break
            else:
                self._job_order.append(job)

        # make a table of all the cycles and jobs
        table = [[''] + [job.get_name() for job in self._job_order] + ['Spares...']]
        for cycle in self._cycles:
            print()
            row = [cycle.get_name()] + [''] * len(self._job_order)
            for person, job in cycle.get_assigned().items():
                row[self._job_order.index(job) + 1] = person.get_name()
            for person in cycle.get_spare_people():
                row.append(person.get_name())
            table.append(row)

        return table
