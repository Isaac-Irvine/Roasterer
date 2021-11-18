import os

from google_sheets import get_roster, upload_roster
from job import Job
from person import Person
from roster7 import Roster
from tkSlots import *

'''
TODO Today:
tune scores
./ when picking up a person, highlight the jobs/slots they can do
./ add in unavailable people
make algorithm account for casually available people
make a jobs table window that lets you pick whos trained and if the job is hard, casual or on the same line
window for making new people and jobs
clean up code a little
package it in such a way that its easy to run
add pickling so you don't need google sheets
add undo redo
'''

roster_undo_states = []


def make_undo_state():
    global roster
    roster_undo_states.append(roster.copy())


def undo():
    global roster
    if roster_undo_states:
        roster = roster_undo_states.pop()
    render_roster(canvas, roster)


roster: Roster = get_roster()

window = tk.Tk()
window.resizable(True, False)
window.title('Rosterer')
print(window.winfo_name())

canvas = tk.Canvas(window, bg='white', height=CELL_SIZE * 5, width=1000)
canvas.pack(expand=True, fill='x')

hbar = tk.Scrollbar(window, orient='horizontal', command=canvas.xview)
hbar.pack(fill='x')
canvas.config(xscrollcommand=hbar.set)

canvas.bind_all("<Button-4>", lambda event: canvas.xview_scroll(-1, 'units'))
canvas.bind_all("<Button-5>", lambda event: canvas.xview_scroll(1, 'units'))


def fill():
    roster.fill()
    render_roster(canvas, roster)


def export():
    bbox = canvas.bbox('all')
    canvas.postscript(file='roster.eps', x=0, y=0, width=bbox[2], height=bbox[3])
    os.popen('open roster.eps')


window.bind_all("Control-z", lambda _: undo())


render_roster(canvas, roster)


fill_button = tk.Button(window, text="Fill", command=fill)
fill_button.pack()
export_button = tk.Button(window, text="Export Image", command=export)
export_button.pack()

tk.mainloop()
