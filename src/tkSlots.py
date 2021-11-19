from time import time
from typing import Callable

from PIL import Image, ImageTk
import tkinter as tk
from os.path import isfile

from job import Job
from person import Person
from roster7 import Roster, Cycle

CELL_SIZE = 80


def make_undo_state():
    pass


def set_undo_state_setter(func: Callable):
    global make_undo_state
    make_undo_state = func


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

    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas):
        self.roster = roster
        self.x = col * CELL_SIZE + CELL_SIZE / 2
        self.y = row * CELL_SIZE + CELL_SIZE / 2
        self.display_x = self.x
        self.display_y = self.y
        self.tk_slots.add(self)
        self.canvas = canvas
        self.rect_obj = canvas.create_rectangle(
            self.display_x - CELL_SIZE / 2,
            self.display_y - CELL_SIZE / 2,
            self.display_x + CELL_SIZE / 2 - 1,
            self.display_y + CELL_SIZE / 2 - 1,
            width=0,
            outline='red'
        )
        self.image_obj = canvas.create_image(self.display_x, self.display_y)
        self.text_obj = canvas.create_text(self.display_x, self.display_y)
        self.tk_objects = [self.rect_obj, self.image_obj, self.text_obj]
        for obj in self.tk_objects:
            canvas.tag_bind(obj, '<Button1-Motion>', self.move)
            canvas.tag_bind(obj, '<ButtonRelease-1>', self.release)

    def move(self, event):
        if not self.movable:
            return
        for tk_slot in TkSlot.tk_slots:
            if tk_slot.can_drag_onto(self) and tk_slot is not self:
                self.canvas.itemconfig(tk_slot.rect_obj, width=1)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for obj in self.tk_objects:
            self.canvas.tag_raise(obj)
            self.canvas.move(obj, x - self.display_x, y - self.display_y)
        self.display_x = x
        self.display_y = y

    def release(self, event):
        if not self.movable:
            return
        for tk_slot in TkSlot.tk_slots:
            self.canvas.itemconfig(tk_slot.rect_obj, width=0)

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        tk_slot = self.get_slot_at(x, y)
        if tk_slot is not self:
            self.dropped_on(tk_slot)
        for obj in self.tk_objects:
            self.canvas.move(obj, self.x - self.display_x, self.y - self.display_y)
        self.display_x = self.x
        self.display_y = self.y

    def dropped_on(self, other: 'TkSlot'):
        pass

    def set_text(self, text: str):
        self.canvas.itemconfig(self.text_obj, text=text)

    def set_image(self, image: ImageTk.PhotoImage):
        self.canvas.itemconfig(self.image_obj, image=image)

    def can_drag_onto(self, other: 'TkSlot') -> bool:
        return False


class TkSlotLabel(TkSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, text: str):
        super().__init__(roster, row, col, canvas)
        self.set_text(text)


class TkJobLabel(TkSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, job: Job):
        super().__init__(roster, row, col, canvas)
        self.job = job
        self.set_text(job.get_name())


class TkCycleLabel(TkSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, cycle: Cycle):
        super().__init__(roster, row, col, canvas)
        self.cycle = cycle
        self.set_text(cycle.get_name())


class TkUnavailableSlot(TkSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, job: Job, cycle: Cycle):
        super().__init__(roster, row, col, canvas)
        self.job = job
        self.cycle = cycle

    def release(self, event):
        make_undo_state()
        self.cycle.jobs.add(self.job)
        render_roster(self.canvas, self.roster)


class TkEmptySlot(TkSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, job: Job, cycle: Cycle):
        super().__init__(roster, row, col, canvas)
        self.job = job
        self.cycle = cycle
        self.canvas.itemconfig(self.rect_obj, fill='#ddd')
        self.set_text('empty')

    def release(self, event):
        make_undo_state()
        self.cycle.jobs.remove(self.job)
        render_roster(self.canvas, self.roster)

    def can_drag_onto(self, other):
        if isinstance(other, TkPersonSlot):
            if other.cycle is self.cycle and other.person.can_do_job(self.job):
                return True
        return False


class TkPersonSlot(TkSlot):
    movable = True
    images: dict[Person, ImageTk.PhotoImage] = {}
    blank_image: ImageTk.PhotoImage = None

    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, cycle: Cycle, person: Person):
        super().__init__(roster, row, col, canvas)
        self.person = person
        self.set_text(person.get_name())
        self.cycle = cycle

        if isfile(f'./images/{person.get_name()}.png'):
            if person in TkPersonSlot.images:
                image = TkPersonSlot.images[person]
            else:
                image = Image.open(f'images/{person.get_name()}.png')
                image = image.resize((CELL_SIZE - 2, CELL_SIZE - 2), Image.ANTIALIAS)
                image = ImageTk.PhotoImage(image)
                TkPersonSlot.images[person] = image
        else:
            if TkPersonSlot.blank_image is None:
                TkPersonSlot.blank_image = ImageTk.PhotoImage(
                    Image.open('./images/blank.png').resize((CELL_SIZE - 1, CELL_SIZE - 1), Image.ANTIALIAS)
                )
            image = TkPersonSlot.blank_image
        self.set_image(image)


class TkAssignedPersonSlot(TkPersonSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, job: Job, cycle: Cycle, person: Person):
        super().__init__(roster, row, col, canvas, cycle, person)
        self.job = job

    def dropped_on(self, other: 'TkSlot'):
        if isinstance(other, TkEmptySlot):
            if self.cycle is not other.cycle:
                return
            make_undo_state()
            self.roster.unassign(self.cycle, self.person)
            self.roster.assign(other.cycle, other.job, self.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkAssignedPersonSlot):
            if self.cycle is not other.cycle:
                return
            make_undo_state()
            self.roster.unassign(self.cycle, self.person)
            self.roster.unassign(other.cycle, other.person)
            self.roster.assign(other.cycle, other.job, self.person)
            self.roster.assign(self.cycle, self.job, other.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkSparePersonSlot) or isinstance(other, TkBlankSparePersonSlot):
            make_undo_state()
            self.roster.unassign(self.cycle, self.person)
            self.cycle.set_casual(self.person, False)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkSpareCasualPersonSlot) or isinstance(other, TkBlankSpareCasualPersonSlot):
            make_undo_state()
            self.roster.unassign(self.cycle, self.person)
            self.cycle.set_casual(self.person, True)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkUnavailablePersonSlot) or isinstance(other, TkBlankUnavailablePersonSlot):
            make_undo_state()
            self.roster.unassign(self.cycle, self.person)
            self.cycle.remove_person(self.person)
            render_roster(self.canvas, self.roster)

    def can_drag_onto(self, other):
        if isinstance(other, TkPersonSlot):
            if other.cycle is self.cycle and other.person.can_do_job(self.job):
                return True
        return False


class TkSparePersonSlot(TkPersonSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, cycle: Cycle, person: Person):
        super().__init__(roster, row, col, canvas, cycle, person)

    def dropped_on(self, other: 'TkSlot'):
        if isinstance(other, TkEmptySlot):
            if self.cycle is not other.cycle:
                return
            make_undo_state()
            self.roster.assign(other.cycle, other.job, self.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkAssignedPersonSlot):
            if self.cycle is not other.cycle:
                return
            make_undo_state()
            self.roster.unassign(other.cycle, other.person)
            self.roster.assign(other.cycle, other.job, self.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkSpareCasualPersonSlot) or isinstance(other, TkBlankSpareCasualPersonSlot):
            make_undo_state()
            self.cycle.set_casual(self.person, True)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkUnavailablePersonSlot) or isinstance(other, TkBlankUnavailablePersonSlot):
            make_undo_state()
            self.cycle.remove_person(self.person)
            render_roster(self.canvas, self.roster)


class TkBlankSparePersonSlot(TkSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, cycle: Cycle):
        super().__init__(roster, row, col, canvas)
        self.cycle = cycle


class TkSpareCasualPersonSlot(TkPersonSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, cycle: Cycle, person: Person):
        super().__init__(roster, row, col, canvas, cycle, person)

    def dropped_on(self, other: 'TkSlot'):
        if isinstance(other, TkEmptySlot):
            if self.cycle is not other.cycle:
                return
            make_undo_state()
            self.roster.assign(other.cycle, other.job, self.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkAssignedPersonSlot):
            if self.cycle is not other.cycle:
                return
            make_undo_state()
            self.roster.unassign(other.cycle, other.person)
            self.roster.assign(other.cycle, other.job, self.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkSparePersonSlot) or isinstance(other, TkBlankSparePersonSlot):
            make_undo_state()
            self.cycle.set_casual(self.person, False)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkUnavailablePersonSlot) or isinstance(other, TkBlankUnavailablePersonSlot):
            make_undo_state()
            self.cycle.remove_person(self.person)
            render_roster(self.canvas, self.roster)


class TkBlankSpareCasualPersonSlot(TkSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, cycle: Cycle):
        super().__init__(roster, row, col, canvas)
        self.cycle = cycle


class TkUnavailablePersonSlot(TkPersonSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, cycle: Cycle, person: Person):
        super().__init__(roster, row, col, canvas, cycle, person)

    def dropped_on(self, other: 'TkSlot'):
        if isinstance(other, TkEmptySlot):
            if self.cycle is not other.cycle:
                return
            make_undo_state()
            self.cycle.fully_available_people.add(self.person)
            self.roster.assign(other.cycle, other.job, self.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkAssignedPersonSlot):
            if self.cycle is not other.cycle:
                return
            make_undo_state()
            self.cycle.fully_available_people.add(self.person)
            self.roster.unassign(other.cycle, other.person)
            self.roster.assign(other.cycle, other.job, self.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkSparePersonSlot) or isinstance(other, TkBlankSparePersonSlot):
            make_undo_state()
            self.cycle.fully_available_people.add(self.person)
            render_roster(self.canvas, self.roster)
        elif isinstance(other, TkSpareCasualPersonSlot) or isinstance(other, TkBlankSpareCasualPersonSlot):
            make_undo_state()
            self.cycle.casually_available_people.add(self.person)
            render_roster(self.canvas, self.roster)


class TkBlankUnavailablePersonSlot(TkSlot):
    def __init__(self, roster: Roster, row: int, col: int, canvas: tk.Canvas, cycle: Cycle):
        super().__init__(roster, row, col, canvas)
        self.cycle = cycle


def render_roster(canvas: tk.Canvas, roster: Roster):
    canvas.delete('all')
    TkSlot.tk_slots.clear()

    # add axis labels
    for col, job in enumerate(roster.jobs, start=1):
        TkJobLabel(roster, 0, col, canvas, job)

    for row, cycle in enumerate(roster.cycles, start=1):
        TkCycleLabel(roster, row, 0, canvas, cycle)

    # add assigned people
    for row, cycle in enumerate(roster.cycles, start=1):
        for col, job in enumerate(roster.jobs, start=1):
            if job not in cycle.jobs:
                TkUnavailableSlot(roster, row, col, canvas, job, cycle)
                continue
            person = roster.get_assinged_person(cycle, job)
            if person is not None:
                TkAssignedPersonSlot(roster, row, col, canvas, job, cycle, person)
            else:
                TkEmptySlot(roster, row, col, canvas, job, cycle)

    # add spare
    max_num_spares = 0
    for cycle in roster.cycles:
        max_num_spares = max(len(roster.get_unassinged_fully_available(cycle)), max_num_spares)
    num_spare_cols = max(1, max_num_spares)

    offset = len(roster.jobs) + 1

    TkSlotLabel(roster, 0, offset, canvas, 'Available...')

    for row, cycle in enumerate(roster.cycles, start=1):
        count = 0
        for col, person in enumerate(roster.get_unassinged_fully_available(cycle), start=offset):
            TkSparePersonSlot(roster, row, col, canvas, cycle, person)
            count += 1
        if count < num_spare_cols:
            for col in range(count + offset, num_spare_cols + offset):
                TkBlankSparePersonSlot(roster, row, col, canvas, cycle)

    # add casual spare
    max_num_casual_spares = 0
    for cycle in roster.cycles:
        max_num_casual_spares = max(len(roster.get_unassinged_casually_available(cycle)), max_num_casual_spares)
    num_casual_spares = max(1, max_num_casual_spares)

    offset = len(roster.jobs) + num_spare_cols + 1

    TkSlotLabel(roster, 0, offset, canvas, 'Casually \navailable...')

    for row, cycle in enumerate(roster.cycles, start=1):
        count = 0
        for col, person in enumerate(roster.get_unassinged_casually_available(cycle), start=offset):
            TkSpareCasualPersonSlot(roster, row, col, canvas, cycle, person)
            count += 1
        if count < num_casual_spares:
            for col in range(count + offset, num_casual_spares + offset):
                TkBlankSpareCasualPersonSlot(roster, row, col, canvas, cycle)

    # add unavailable spare
    max_num_unavailable_spares = 0
    for cycle in roster.cycles:
        max_num_unavailable_spares = max(len(roster.get_unavailable(cycle)), max_num_unavailable_spares)
    num_unavailable_spares = max(1, max_num_unavailable_spares)

    offset = len(roster.jobs) + num_spare_cols + num_casual_spares + 1

    TkSlotLabel(roster, 0, offset, canvas, 'Unavailable...')

    for row, cycle in enumerate(roster.cycles, start=1):
        count = 0
        for col, person in enumerate(roster.get_unavailable(cycle), start=offset):
            TkUnavailablePersonSlot(roster, row, col, canvas, cycle, person)
            count += 1
        if count < num_unavailable_spares:
            for col in range(count + offset, num_unavailable_spares + offset):
                TkBlankUnavailablePersonSlot(roster, row, col, canvas, cycle)

    canvas.configure(scrollregion=canvas.bbox("all"))
