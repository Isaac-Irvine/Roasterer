from time import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tabulate import tabulate

from slot import PotentialSlots
from table_parsing import parse_table


# connect to google sheets and download roaster data
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('rostering-2021-5cb1f556a1a5.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open('Roster')
jobs_cycles = spreadsheet.get_worksheet_by_id(0).get_values()
people_jobs = spreadsheet.get_worksheet_by_id(1319304401).get_values()
people_availability = spreadsheet.get_worksheet_by_id(2017819441).get_values()
roster_hard_coding = spreadsheet.get_worksheet_by_id(940515330).get_values()
roster_sheet = spreadsheet.get_worksheet_by_id(1316761516)


def get_roaster():
    return parse_table(jobs_cycles, people_availability, people_jobs, roster_hard_coding)


def upload_roster(roster):
    roster_as_table = roster.to_table()
    cells = []
    for row_num, row in enumerate(roster_as_table):
        for col_num, cell in enumerate(row):
            cells.append(gspread.Cell(row_num + 1, col_num + 1, roster_as_table[row_num][col_num]))
    roster_sheet.clear()
    roster_sheet.update_cells(cells)
