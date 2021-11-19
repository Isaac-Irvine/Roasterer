from tkinter import Toplevel, Label

from roster7 import Roster


class EditPeople(Toplevel):
    def __init__(self, master, roster: Roster):
        super().__init__(master=master)

        self.roster = roster

        self.title('Edit Jobs and People')
        self.geometry('400x400')
        self.attributes('-topmost', True)
        label = Label(self, text='This is a new Window')
        label.pack()
