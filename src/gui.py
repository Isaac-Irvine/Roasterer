import os
import pickle
from tkinter import filedialog as fd, Menu, Toplevel, Label, Checkbutton, IntVar, StringVar, Entry, Button, Frame, \
    BooleanVar

from tkSlots import *

'''
TODO:
implement jobs edit window
make jobs and person add window
way to change order of jobs
package it in such a way that its easy to run
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


class PersonWindow:
    def __init__(self, person: Person):
        self.person = person
        self.window = None
        self.name_var = StringVar(value=person.get_name())

    def close(self, event=None):
        self.window.destroy()

    def save_and_close(self, event=None):
        self.person.set_name(self.name_var.get())
        self.close()
        render_roster(canvas, roster)
        render_edit_window_table()

    def delete_and_close(self, event=None):
        roster.remove_person(self.person)
        self.close()
        render_roster(canvas, roster)
        render_edit_window_table()

    def open(self, event=None):
        self.window = Toplevel(window)
        self.window.title(f'Edit {self.person.get_name()}')
        self.window.resizable(False, False)

        fields_frame = Frame(self.window)
        fields_frame.pack()

        # Name
        Label(fields_frame, text='Name:').grid(row=0, column=0)
        Entry(fields_frame, textvariable=self.name_var).grid(row=0, column=1)

        # buttons
        Button(
            self.window,
            text='Delete person',
            fg='red',
            command=lambda: self.delete_and_close()
        ).pack(side='left')
        Button(
            self.window,
            text='Okay',
            command=lambda: self.save_and_close()
        ).pack(side='right')


class JobsWindow:
    def __init__(self, job: Job):
        self.job = job
        self.window = None
        self.name_var = StringVar(value=job.get_name())
        if job.get_job_group() is None:
            self.group_var = StringVar()
        else:
            self.group_var = StringVar(value=job.get_job_group().get_name())
        self.hard_var = BooleanVar(value=job.is_hard())
        self.casual_var = BooleanVar(value=job.is_hard())

    def close(self):
        self.window.destroy()

    def save_and_close(self, event=None):
        self.job.set_name(self.name_var.get())
        self.job.set_casual(self.casual_var.get())
        self.job.set_hard(self.hard_var.get())
        self.close()
        render_roster(canvas, roster)
        render_edit_window_table()

    def delete_and_close(self, event=None):
        roster.remove_job(self.job)
        self.close()
        render_roster(canvas, roster)
        render_edit_window_table()

    def open(self, event=None):
        self.window = Toplevel(window)
        self.window.title(f'Edit {self.job.get_name()}')
        self.window.resizable(False, False)

        fields_frame = Frame(self.window)
        fields_frame.pack()

        # Name
        Label(fields_frame, text='Name:').grid(row=0, column=0)
        Entry(fields_frame, textvariable=self.name_var).grid(row=0, column=1)

        # Group TODO: add dropdown
        Label(fields_frame, text='Group:').grid(row=1, column=0)
        Entry(fields_frame, textvariable=self.group_var).grid(row=1, column=1)

        # Hard
        Label(fields_frame, text='Is hard:').grid(row=2, column=0)
        Checkbutton(fields_frame, variable=self.hard_var).grid(row=2, column=1)

        # Casual
        Label(fields_frame, text='Is casual:').grid(row=3, column=0)
        Checkbutton(fields_frame, variable=self.casual_var).grid(row=3, column=1)

        # buttons
        Button(
            self.window,
            text='Delete job',
            fg='red',
            command=lambda: self.delete_and_close()
        ).pack(side='left')
        Button(
            self.window,
            text='Okay',
            command=lambda: self.save_and_close()
        ).pack(side='right')


def render_edit_window_table():
    global roster
    global edit_window

    for widget in edit_window.winfo_children():
        widget.destroy()

    for row, person in enumerate(roster.people, start=1):
        label = Label(edit_window, text=person.get_name())
        label.grid(row=row, column=0)
        person_window = PersonWindow(person)
        label.bind('<Double-Button-1>', person_window.open)
    for col, job in enumerate(roster.jobs, start=1):
        label = Label(edit_window, text=job.get_name())
        label.grid(row=0, column=col)
        job_window = JobsWindow(job)
        label.bind('<Double-Button-1>', job_window.open)
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
file_menu.add_command(label='Export Image', command=export)

edit_menu = Menu(menu)
menu.add_cascade(label='Edit', menu=edit_menu)
edit_menu.add_command(label='Undo', command=undo)
edit_menu.add_command(label='Edit training', command=open_edit_window)
edit_menu.add_command(label='Add person')
edit_menu.add_command(label='Add job')

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
