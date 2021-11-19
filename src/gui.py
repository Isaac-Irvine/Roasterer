import os
import pickle
from tkinter import filedialog as fd, Menu, Toplevel, Label, Checkbutton, IntVar, StringVar, Entry, Button, Frame, \
    BooleanVar

from edit_people_gui import EditPeople
from tkSlots import *

'''
TODO Today:
./ make algorithm account for casually available people
make a jobs table window that lets you pick whos trained and if the job is hard, casual or on the same line
window for making new people and jobs
package it in such a way that its easy to run
./ tune scores. Could still do with some more tuning
./ when picking up a person, highlight the jobs/slots they can do
./ add in unavailable people
./ disable and enable slots
clean up code a little
./ add pickling so you don't need google sheets
./ add undo
add higher quality render for image exports
'''

roster: Roster = Roster()

roster_undo_states = []


def make_undo_state():
    global roster
    global roster_undo_states
    roster_undo_states.append(roster.deep_copy())
    if len(roster_undo_states) > 50:
        roster_undo_states.pop(0)


set_undo_state_setter(make_undo_state)


def undo():
    global roster
    global roster_undo_states
    if roster_undo_states:
        roster = roster_undo_states.pop()
        render_roster(canvas, roster)


def fill():
    make_undo_state()
    roster.fill()
    render_roster(canvas, roster)


def export():
    global roster
    filename = fd.asksaveasfilename(
        filetypes=(
            ('Post Script', '*.eps'),
            ('All files', '*.*')
        )
    )
    if filename != '':
        bbox = canvas.bbox('all')
        canvas.postscript(file=filename, x=0, y=0, width=bbox[2], height=bbox[3])
        os.popen(f'open {filename}')


def open_roster():
    global roster
    filename = fd.askopenfilename(
        filetypes=(
            ('Roster files', '*.roster'),
            ('All files', '*.*')
        )
    )
    if filename != '':
        roster_undo_states.clear()
        with open(filename, 'rb') as file:
            roster = pickle.load(file)
        render_roster(canvas, roster)
        render_edit_window_table()


def save_roster():
    global roster
    filename = fd.asksaveasfilename(
        filetypes=(
            ('Roster files', '*.roster'),
            ('All files', '*.*')
        )
    )
    if filename != '':
        with open(filename, 'wb') as file:
            pickle.dump(roster, file)


def open_edit_window():
    global edit_window
    edit_window.deiconify()


def close_edit_window():
    edit_window.withdraw()


def get_toggle(person, job):
    def toggle_job():
        if person.can_do_job(job):
            person.remove_job(job)
        else:
            person.add_job(job)
    return toggle_job


def person_window_factory(master_window, person: Person, label: Label):
    window = None
    name_var = StringVar(value=person.get_name())

    def close_window():
        global window
        window.destroy()
        person.set_name(name_var.get())
        label.config(text=name_var.get())
        render_roster(canvas, roster)

    def open_window(event):
        global window
        window = Toplevel(master_window)
        window.title(f'Edit {person.get_name()}')
        window.resizable(False, False)

        fields_frame = Frame(window)
        fields_frame.pack()

        # Name
        Label(fields_frame, text='Name:').grid(row=0, column=0)
        Entry(fields_frame, textvariable=name_var).grid(row=0, column=1)

        # buttons
        Button(window, text='Delete person', fg='red').pack(side='left')
        Button(
            window,
            text='Okay',
            command=close_window
        ).pack(side='right')
    return open_window


def job_window_factory(master_window, job: Job, label: Label):
    window = None
    name_var = StringVar(value=job.get_name())
    if job.get_job_group() is None:
        group_var = StringVar()
    else:
        group_var = StringVar(value=job.get_job_group().get_name())
    hard_var = BooleanVar(value=job.is_hard())
    casual_var = BooleanVar(value=job.is_hard())

    def close_window():
        global window
        window.destroy()
        job.set_name(name_var.get())
        label.config(text=name_var.get())
        render_roster(canvas, roster)

    def open_window(event):
        global window
        window = Toplevel(master_window)
        window.title(f'Edit {job.get_name()}')
        window.resizable(False, False)

        fields_frame = Frame(window)
        fields_frame.pack()

        # Name
        Label(fields_frame, text='Name:').grid(row=0, column=0)
        Entry(fields_frame, textvariable=name_var).grid(row=0, column=1)

        # Group TODO: add dropdown
        Label(fields_frame, text='Group:').grid(row=1, column=0)
        Entry(fields_frame, textvariable=group_var).grid(row=1, column=1)

        # Hard
        Label(fields_frame, text='Is hard:').grid(row=2, column=0)
        Checkbutton(fields_frame, variable=hard_var).grid(row=2, column=1)

        # Casual
        Label(fields_frame, text='Is casual:').grid(row=3, column=0)
        Checkbutton(fields_frame, variable=casual_var).grid(row=3, column=1)

        # buttons
        Button(window, text='Delete job', fg='red').pack(side='left')
        Button(
            window,
            text='Okay',
            command=close_window
        ).pack(side='right')
    return open_window


def render_edit_window_table():
    global roster
    global edit_window

    for row, person in enumerate(roster.people, start=1):
        label = Label(edit_window, text=person.get_name())
        label.grid(row=row, column=0)
        label.bind('<Double-Button-1>', person_window_factory(edit_window, person, label))
    for col, job in enumerate(roster.jobs, start=1):
        label = Label(edit_window, text=job.get_name())
        label.grid(row=0, column=col)
        label.bind('<Double-Button-1>', job_window_factory(edit_window, job, label))
    for row, person in enumerate(roster.people, start=1):
        for col, job in enumerate(roster.jobs, start=1):
            checkbox = Checkbutton(edit_window, command=get_toggle(person, job))
            checkbox.grid(row=row, column=col)
            if person.can_do_job(job):
                checkbox.select()


# window
window = tk.Tk()
window.resizable(True, False)
window.title('Rosterer')

# file menu
menu = Menu(window)
window.config(menu=menu)
file_menu = Menu(menu)
menu.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label='Open', command=open_roster)
file_menu.add_command(label='Save', command=save_roster)
file_menu.add_command(label='Undo', command=undo)
file_menu.add_command(label='Export Image', command=export)
file_menu.add_command(label='Edit people and jobs', command=open_edit_window)

# key binds
window.bind_all('<Control-z>', lambda _: undo())
window.bind_all('<Command-z>', lambda _: undo())

# all the slots
canvas = tk.Canvas(window, bg='white', height=CELL_SIZE * 5, width=1000)
canvas.pack(expand=True, fill='x')
render_roster(canvas, roster)

# scroll bar for slots
hbar = tk.Scrollbar(window, orient='horizontal', command=canvas.xview)
hbar.pack(fill='x')
canvas.config(xscrollcommand=hbar.set)

canvas.bind_all("<Button-4>", lambda event: canvas.xview_scroll(-1, 'units'))
canvas.bind_all("<Button-5>", lambda event: canvas.xview_scroll(1, 'units'))

# bottom buttons
fill_button = tk.Button(window, text="Fill", command=fill)
fill_button.pack()


# edit people and jobs window
edit_window = Toplevel(window)
edit_window.resizable(False, False)
edit_window.title('Edit People and Jobs')
edit_window.withdraw()
edit_window.protocol("WM_DELETE_WINDOW", close_edit_window)

render_edit_window_table()

tk.mainloop()
