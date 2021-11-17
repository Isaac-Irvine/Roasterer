import os
import tkinter as tk
from os.path import isfile

from PIL import Image, ImageTk

from google_sheets import get_roaster, upload_roster
from src.cycle import Cycle
from src.job import Job
from src.person import Person
from src.slot import Slot

CELL_SIZE = 80

roster = get_roaster()

window = tk.Tk()
window.resizable(True, False)


canvas = tk.Canvas(window, bg='white', height=CELL_SIZE * 5, width=1000)
canvas.pack(expand=True, fill='x')

hbar = tk.Scrollbar(window, orient='horizontal', command=canvas.xview)
hbar.pack(fill='x')
canvas.config(xscrollcommand=hbar.set)

canvas.bind_all("<Button-4>", lambda event: canvas.xview_scroll(-1, 'units'))
canvas.bind_all("<Button-5>", lambda event: canvas.xview_scroll(1, 'units'))


class TkSlot:
    movable = False
    tk_slots: set['TkSlot'] = set()

    @staticmethod
    def get_slot_at(x: int, y: int) -> 'TkSlot':
        for tk_slot in TkSlot.tk_slots:
            if (
                    tk_slot.x - CELL_SIZE / 2 < x < tk_slot.x + CELL_SIZE / 2
                    and tk_slot.y - CELL_SIZE / 2 < y < tk_slot.y + CELL_SIZE / 2
            ):
                return tk_slot

    def __init__(self, row: int, col: int, canvas: tk.Canvas):
        self.x = col * CELL_SIZE + CELL_SIZE / 2
        self.y = row * CELL_SIZE + CELL_SIZE / 2
        self.display_x = self.x
        self.display_y = self.y
        self.tk_slots.add(self)
        self.canvas = canvas
        self.image_obj = canvas.create_image(self.display_x, self.display_y)
        self.text_obj = canvas.create_text(self.display_x, self.display_y)
        canvas.tag_bind(self.image_obj, '<Button1-Motion>', self.move)
        canvas.tag_bind(self.image_obj, '<ButtonRelease-1>', self.release)
        canvas.tag_bind(self.text_obj, '<Button1-Motion>', self.move)
        canvas.tag_bind(self.text_obj, '<ButtonRelease-1>', self.release)

    def move(self, event):
        if not self.movable:
            return
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        self.canvas.tag_raise(self.image_obj)
        self.canvas.tag_raise(self.text_obj)
        self.canvas.move(self.image_obj, x - self.display_x, y - self.display_y)
        self.canvas.move(self.text_obj, x - self.display_x, y - self.display_y)
        self.display_x = x
        self.display_y = y

    def release(self, event):
        if not self.movable:
            return
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        tk_slot = self.get_slot_at(x, y)
        if tk_slot is not self:
            self.dropped_on(tk_slot)
        self.canvas.move(self.image_obj, self.x - self.display_x, self.y - self.display_y)
        self.canvas.move(self.text_obj, self.x - self.display_x, self.y - self.display_y)
        self.display_x = self.x
        self.display_y = self.y

    def dropped_on(self, other: 'TkSlot'):
        pass

    def set_text(self, text: str):
        self.canvas.itemconfig(self.text_obj, text=text)

    def set_image(self, image: ImageTk.PhotoImage):
        self.canvas.itemconfig(self.image_obj, image=image)


class TkEmptySlot(TkSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, slot: Slot):
        super().__init__(row, col, canvas)
        self.slot = slot
        self.set_text('empty')


class TkSlotLabel(TkSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, text: str):
        super().__init__(row, col, canvas)
        self.set_text(text)


class TkJobLabel(TkSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, job: Job):
        super().__init__(row, col, canvas)
        self.job = job
        self.set_text(job.get_name())


class TkCycleLabel(TkSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, cycle: Cycle):
        super().__init__(row, col, canvas)
        self.cycle = cycle
        self.set_text('empty')


class TkUnavailableSlot(TkSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, job: Job, cycle: Cycle):
        super().__init__(row, col, canvas)
        self.job = job
        self.cycle = cycle
        self.set_text('not needed')


class TkPersonSlot(TkSlot):
    movable = True
    images: dict[Person, ImageTk.PhotoImage] = {}
    blank_image = ImageTk.PhotoImage(
        Image.open('images/blank.png').resize((CELL_SIZE - 1, CELL_SIZE - 1), Image.ANTIALIAS)
    )

    def __init__(self, row: int, col: int, canvas: tk.Canvas, person: Person):
        super().__init__(row, col, canvas)
        self.person = person
        self.set_text(person.get_name())

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
        self.set_image(image)


class TkAssignedPersonSlot(TkPersonSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, slot: Slot, person: Person):
        super().__init__(row, col, canvas, person)
        self.slot = slot

    def dropped_on(self, other: 'TkSlot'):
        if isinstance(other, TkEmptySlot):
            if self.slot.cycle is not other.slot.cycle:
                return
            roster.unassign(self.slot)
            roster.assign(self.person, other.slot)
            render_roster()
        elif isinstance(other, TkAssignedPersonSlot):
            if self.slot.cycle is not other.slot.cycle:
                return
            roster.unassign(self.slot)
            roster.unassign(other.slot)
            roster.assign(self.person, other.slot)
            roster.assign(other.person, self.slot)
            render_roster()
        elif isinstance(other, TkSparePersonSlot) or isinstance(other, TkBlankSparePersonSlot):
            roster.unassign(self.slot)
            self.slot.cycle.set_casual(self.person, False)
            render_roster()
        elif isinstance(other, TkSpareCasualPersonSlot) or isinstance(other, TkBlankSpareCasualPersonSlot):
            roster.unassign(self.slot)
            self.slot.cycle.set_casual(self.person, True)
            render_roster()


class TkSparePersonSlot(TkPersonSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, cycle: Cycle, person: Person):
        super().__init__(row, col, canvas, person)
        self.cycle = cycle

    def dropped_on(self, other: 'TkSlot'):
        if isinstance(other, TkEmptySlot):
            if self.cycle is not other.slot.cycle:
                return
            roster.assign(self.person, other.slot)
            render_roster()
        elif isinstance(other, TkAssignedPersonSlot):
            if self.cycle is not other.slot.cycle:
                return
            roster.unassign(other.slot)
            roster.assign(self.person, other.slot)
            render_roster()
        elif isinstance(other, TkSpareCasualPersonSlot) or isinstance(other, TkBlankSpareCasualPersonSlot):
            self.cycle.set_casual(self.person, True)
            render_roster()


class TkBlankSparePersonSlot(TkSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, cycle: Cycle):
        super().__init__(row, col, canvas)
        self.cycle = cycle


class TkSpareCasualPersonSlot(TkPersonSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, cycle: Cycle, person: Person):
        super().__init__(row, col, canvas, person)
        self.cycle = cycle

    def dropped_on(self, other: 'TkSlot'):
        if isinstance(other, TkEmptySlot):
            if self.cycle is not other.slot.cycle:
                return
            roster.assign(self.person, other.slot)
            render_roster()
        elif isinstance(other, TkAssignedPersonSlot):
            if self.cycle is not other.slot.cycle:
                return
            roster.unassign(other.slot)
            roster.assign(self.person, other.slot)
            render_roster()
        elif isinstance(other, TkSparePersonSlot) or isinstance(other, TkBlankSparePersonSlot):
            self.cycle.set_casual(self.person, False)
            render_roster()


class TkBlankSpareCasualPersonSlot(TkSlot):
    def __init__(self, row: int, col: int, canvas: tk.Canvas, cycle: Cycle):
        super().__init__(row, col, canvas)
        self.cycle = cycle


def render_roster():
    canvas.delete('all')
    TkSlot.tk_slots.clear()

    # add axis labels
    for col, job in enumerate(roster.get_jobs(), start=1):
        TkJobLabel(0, col, canvas, job)

    for row, cycle in enumerate(roster.get_cycles(), start=1):
        TkJobLabel(row, 0, canvas, cycle)

    # add assigned people
    for row, cycle in enumerate(roster.get_cycles(), start=1):
        for col, job in enumerate(roster.get_jobs(), start=1):
            slot = roster.get_slot(job, cycle)
            if slot is None:
                TkUnavailableSlot(row, col, canvas, job, cycle)
            elif slot in roster.get_assigned():
                TkAssignedPersonSlot(row, col, canvas, slot, roster.get_assigned()[slot])
            else:
                TkEmptySlot(row, col, canvas, slot)

    # add spare
    max_num_spares = 0
    for cycle in roster.get_cycles():
        max_num_spares = max(len(roster.get_available(cycle)), max_num_spares)
    num_spare_cols = max(1, max_num_spares)
    offset = len(roster.get_jobs()) + 1
    TkSlotLabel(0, offset, canvas, 'available...')
    for row, cycle in enumerate(roster.get_cycles(), start=1):
        count = 0
        for col, person in enumerate(roster.get_available(cycle), start=offset):
            TkSparePersonSlot(row, col, canvas, cycle, person)
            count += 1
        if count < num_spare_cols:
            for col in range(count + offset, num_spare_cols + offset):
                TkBlankSparePersonSlot(row, col, canvas, cycle)

    # add casual spare
    max_num_casual_spares = 0
    for cycle in roster.get_cycles():
        max_num_casual_spares = max(len(roster.get_casually_available(cycle)), max_num_casual_spares)
    num_casual_spares = max(1, max_num_casual_spares)
    offset = len(roster.get_jobs()) + num_spare_cols + 1
    TkSlotLabel(0, offset, canvas, 'Casually \navailable...')
    for row, cycle in enumerate(roster.get_cycles(), start=1):
        count = 0
        for col, person in enumerate(roster.get_casually_available(cycle), start=offset):
            TkSpareCasualPersonSlot(row, col, canvas, cycle, person)
            count += 1
        if count < num_casual_spares:
            for col in range(count + offset, num_casual_spares + offset):
                TkBlankSpareCasualPersonSlot(row, col, canvas, cycle)

    canvas.configure(scrollregion=canvas.bbox("all"))


def fill():
    roster.fill()
    render_roster()


def upload():
    upload_roster(roster)


def save():
    bbox = canvas.bbox('all')
    canvas.postscript(file='roster.eps', x=0, y=0, width=bbox[2], height=bbox[3])
    os.popen('open roster.eps')


def score():
    print('score:', roster.score())


render_roster()


fill_button = tk.Button(window, text="Fill", command=fill)
fill_button.pack()
upload_button = tk.Button(window, text="Upload", command=upload)
upload_button.pack()
upload_button = tk.Button(window, text="Save", command=save)
upload_button.pack()
score_button = tk.Button(window, text="score", command=score)
score_button.pack()

tk.mainloop()
