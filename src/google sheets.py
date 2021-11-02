import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tabulate import tabulate

from table_parsing import parse_table

print('connecting to google sheets')

# connect to google sheets and download roaster data
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('rostering-2021-5cb1f556a1a5.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open('Roaster')
jobs_cycles = spreadsheet.get_worksheet_by_id(0).get_values()
people_jobs = spreadsheet.get_worksheet_by_id(1319304401).get_values()
people_availability = spreadsheet.get_worksheet_by_id(2017819441).get_values()
roaster_hard_coding = spreadsheet.get_worksheet_by_id(940515330).get_values()
roaster_sheet = spreadsheet.get_worksheet_by_id(1316761516)

print('got all google data')

roaster, cycles, jobs = parse_table(jobs_cycles, people_availability, people_jobs, roaster_hard_coding)

print('starting finder')
roaster.fill()
roaster_as_table = roaster.to_table(cycles, jobs)

print(tabulate(roaster_as_table, headers='firstrow'))

# put on google sheets
cells = []
for row_num, row in enumerate(roaster_as_table):
    for col_num, cell in enumerate(row):
        cells.append(gspread.Cell(row_num + 1, col_num + 1, roaster_as_table[row_num][col_num]))
roaster_sheet.clear()
roaster_sheet.update_cells(cells)
