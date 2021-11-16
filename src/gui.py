import tkinter as tk
from os.path import isfile
from types import NoneType

from PIL import Image, ImageTk

from google_sheets import get_roaster, upload_roster
from src.cycle import Cycle
from src.job import Job
from src.person import Person
from src.slot import Slot

CELL_SIZE = 80

roster = get_roaster()

window = tk.Tk()


canvas = tk.Canvas(window, bg='white')
canvas.pack(fill='both', expand=True)


class TkSlot:
    images: dict[Person, ImageTk.PhotoImage] = {}
    blank_image = ImageTk.PhotoImage(
        Image.open('images/blank.png').resize((CELL_SIZE - 1, CELL_SIZE - 1), Image.ANTIALIAS)
        )

    tk_slots: set['TkSlot'] = set()

    @staticmethod
    def get_slot_at(x: int, y: int) -> 'TkSlot':
        for tk_slot in TkSlot.tk_slots:
            if (
                    tk_slot.x - CELL_SIZE / 2 < x < tk_slot.x + CELL_SIZE / 2
                    and tk_slot.y - CELL_SIZE / 2 < y < tk_slot.y + CELL_SIZE / 2
            ):
                return tk_slot

    @staticmethod
    def update():
        for tk_slot in TkSlot.tk_slots:
            if tk_slot.slot is not None:
                if tk_slot.slot in roster.get_assigned():
                    tk_slot.set_person(roster.get_assigned()[tk_slot.slot])
                else:
                    tk_slot.set_person(None)
            else:
                tk_slot.set_person(None)

    def __init__(self, job: Job, cycle: Cycle, person: Person, canvas: tk.Canvas, roster, x, y):
        self.roster = roster
        self.tk_slots.add(self)
        self.canvas = canvas
        self.x = x
        self.y = y
        self.display_x = self.x
        self.display_y = self.y
        self.job = job
        self.cycle = cycle
        self.slot = roster.get_slot(job, cycle)
        self.image_obj = canvas.create_image(self.display_x, self.display_y)
        self.text_obj = canvas.create_text(self.display_x, self.display_y, text='n/a' if self.slot is None else 'empty')
        canvas.tag_bind(self.image_obj, '<Button1-Motion>', self.move)
        canvas.tag_bind(self.image_obj, '<ButtonRelease-1>', self.release)
        canvas.tag_bind(self.text_obj, '<Button1-Motion>', self.move)
        canvas.tag_bind(self.text_obj, '<ButtonRelease-1>', self.release)
        self.person = person
        if person is not None:
            self.set_person(person)

    def set_person(self, person: Person):
        self.person = person
        if person is None:
            self.canvas.itemconfig(self.image_obj, image=tk.PhotoImage())  # TODO: fix this
            self.canvas.itemconfig(self.text_obj, text='n/a' if self.slot is None else 'empty')
            return

        if isfile(f'./images/{person.get_name()}.png'):
            if person in self.images:
                image = self.images[person]
            else:
                image = Image.open(f'images/{person.get_name()}.png')
                image = image.resize((CELL_SIZE - 1, CELL_SIZE - 1), Image.ANTIALIAS)
                image = ImageTk.PhotoImage(image)
                self.images[person] = image
        else:
            image = self.blank_image
        self.canvas.itemconfig(self.image_obj, image=image)
        self.canvas.itemconfig(self.text_obj, text=person.get_name())

    def release(self, event):
        if self.person is None:
            return
        dropped_on = self.get_slot_at(event.x, event.y)
        if dropped_on is not None and dropped_on.cycle is self.cycle:
            person = dropped_on.person
            dropped_on.set_person(self.person)
            self.set_person(person)
            if self.slot is not None:
                if self.slot in roster.get_assigned():
                    roster.unassign(self.slot)
                if self.person is not None:
                    roster.assign(self.person, self.slot)
            if dropped_on.slot is not None:
                if dropped_on.slot in roster.get_assigned():
                    roster.unassign(dropped_on.slot)
                if dropped_on.person is not None:
                    roster.assign(dropped_on.person, dropped_on.slot)
        self.canvas.move(self.image_obj, self.x - self.display_x, self.y - self.display_y)
        self.canvas.move(self.text_obj, self.x - self.display_x, self.y - self.display_y)
        self.display_x = self.x
        self.display_y = self.y

    def move(self, event):
        if self.person is None:
            return
        self.canvas.tag_raise(self.image_obj)
        self.canvas.tag_raise(self.text_obj)
        self.canvas.move(self.image_obj, event.x - self.display_x, event.y - self.display_y)
        self.canvas.move(self.text_obj, event.x - self.display_x, event.y - self.display_y)
        self.display_x = event.x
        self.display_y = event.y


# add axis labels
for i, job in enumerate(roster.get_jobs()):
    text = job.get_name()
    if job.get_job_group() is not None:
        text += '\n' + job.get_job_group().get_name()
    if job.is_hard():
        text += '\nhard'
    if job.is_casual():
        text += '\ncasual'
    text += '\n' * (3 - text.count('\n'))

    canvas.create_text(
        (i + 1) * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE / 2,
        text=text
    )
for i, cycle in enumerate(roster.get_cycles()):
    canvas.create_text(CELL_SIZE / 2, (i + 1) * CELL_SIZE + CELL_SIZE / 2, text=cycle.get_name())

# add assigned people
for i, cycle in enumerate(roster.get_cycles()):
    for j, job in enumerate(roster.get_jobs()):
        x = (j + 1) * CELL_SIZE + CELL_SIZE / 2
        y = (i + 1) * CELL_SIZE + CELL_SIZE / 2
        slot = roster.get_slot(job, cycle)
        if slot is not None and slot in roster.get_assigned():
            TkSlot(job, cycle, roster.get_assigned()[slot], canvas, roster, x, y)
        else:
            TkSlot(job, cycle, None, canvas, roster, x, y)


# add available people
available_x_start = len(roster.get_jobs()) + 1
canvas.create_text(available_x_start * CELL_SIZE + CELL_SIZE / 2, CELL_SIZE / 2, text='Spare...')
for i, cycle in enumerate(roster.get_cycles()):
    for j, person in enumerate(roster.get_available(cycle)):
        x = (j + available_x_start) * CELL_SIZE + CELL_SIZE / 2
        y = (i + 1) * CELL_SIZE + CELL_SIZE / 2
        TkSlot(None, cycle, person, canvas, roster, x, y)


def fill():
    roster.fill()
    TkSlot.update()
    canvas.update()


def upload():
    upload_roster(roster)


fill_button = tk.Button(window, text="Fill", command=fill)
fill_button.pack()
upload_button = tk.Button(window, text="Uplaod", command=upload)
upload_button.pack()

tk.mainloop()
