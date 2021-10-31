from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tabulate import tabulate

from cycle import Cycle
from finder import find_roaster
from job import Job
from person import Person
from roaster import Roaster
from time import time

print('connecting to google sheets')

# connect to google sheets and download roaster data
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('rostering-2021-5cb1f556a1a5.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open("Roaster_input_data")
jobs_cycles_sheet = spreadsheet.get_worksheet_by_id(0).get_values()
people_jobs_sheet = spreadsheet.get_worksheet_by_id(1319304401).get_values()
people_availability_sheet = spreadsheet.get_worksheet_by_id(2017819441).get_values()

print("got all google data")


def to_bool(string):
    if string == 'TRUE':
        return True
    elif string == 'FALSE':
        return False
    raise RuntimeError('Cell is not TRUE or FALSE')


# parse jobs v cycles table
jobs = {}

cycle_1 = Cycle("cycle 1")
cycle_2 = Cycle("cycle 2")
cycle_3 = Cycle("cycle 3")
cycle_4 = Cycle("cycle 4")

for row in filter(lambda r: r[0] != '', jobs_cycles_sheet[1:]):
    job = Job(row[0], to_bool(row[1]))
    jobs[row[0]] = job

    if to_bool(row[2]):
        cycle_1.add_job(job)
    if to_bool(row[3]):
        cycle_2.add_job(job)
    if to_bool(row[4]):
        cycle_3.add_job(job)
    if to_bool(row[5]):
        cycle_4.add_job(job)

    # TODO: do something with wild cards

# parse people v availability jobs table
people = {}
for row in filter(lambda r: r[0] != '', people_availability_sheet[1:]):
    name = row[0]
    person = Person(name)
    people[name] = person

    if to_bool(row[1]):
        cycle_1.add_person(person)
    if to_bool(row[2]):
        cycle_2.add_person(person)
    if to_bool(row[3]):
        cycle_3.add_person(person)
    if to_bool(row[4]):
        cycle_4.add_person(person)

# parse people v jobs table
jobs_list = people_jobs_sheet[0]

for row in filter(lambda r: r[0] != '', people_jobs_sheet[1:]):
    person = people[row[0]]  # todo: data validation
    for i in range(1, len(row)):
        if row[i] != '':
            job = jobs[jobs_list[i]]
            person.add_job(job, row[i] == 'Trainee')
            if row[i] == 'Trainer':
                person.add_job(job.get_trainer_job())


start_time = time()
roaster = find_roaster(Roaster([cycle_1, cycle_2, cycle_3, cycle_4]))
print(f"time taken: {time() - start_time}s")
print(tabulate(roaster.to_table(), headers="firstrow"))
