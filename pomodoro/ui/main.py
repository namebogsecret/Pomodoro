import tkinter as tk
from tkinter import messagebox
from ..utils.sound import play_sound
from ..config import WORK_TIME_MIN, BREAK_TIME_MIN

class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        self.master.title("Pomodoro Timer")
        self.master.resizable(False, False)

        self.work_time = WORK_TIME_MIN * 60
        self.break_time = BREAK_TIME_MIN * 60
        self.is_working = True
        self.timer_running = False
        self.time_left = self.work_time

        self.create_widgets()
        self.settings_frame.grid_remove()
        self.settings_visible = not self.settings_visible

    def create_widgets(self):
        self.label = tk.Label(self.master, text="Work Time", font=("Helvetica", 24))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.time_label = tk.Label(self.master, text=self.format_time(self.time_left), font=("Helvetica", 48))
        self.time_label.grid(row=1, column=0, columnspan=2, pady=10)

        self.settings_frame = tk.Frame(self.master)
        self.settings_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.work_time_label = tk.Label(self.settings_frame, text="Work time (minutes):", font=("Helvetica", 14))
        self.work_time_label.grid(row=0, column=0, padx=5, pady=5)
        self.work_time_entry = tk.Entry(self.settings_frame, font=("Helvetica", 14))
        self.work_time_entry.grid(row=0, column=1, padx=5, pady=5)
        self.work_time_entry.insert(0, str(self.work_time // 60))
        self.work_time_entry.bind("<FocusIn>", self.select_all_text)
        self.work_time_entry.bind("<KeyRelease>", self.update_times)

        self.break_time_label = tk.Label(self.settings_frame, text="Break time (minutes):", font=("Helvetica", 14))
        self.break_time_label.grid(row=1, column=0, padx=5, pady=5)
        self.break_time_entry = tk.Entry(self.settings_frame, font=("Helvetica", 14))
        self.break_time_entry.grid(row=1, column=1, padx=5, pady=5)
        self.break_time_entry.insert(0, str(self.break_time // 60))
        self.break_time_entry.bind("<FocusIn>", self.select_all_text)
        self.break_time_entry.bind("<KeyRelease>", self.update_times)

        self.toggle_button = tk.Button(self.master, text="Show Settings", command=self.toggle_settings, font=("Helvetica", 14)) # на английском показать/скрыть настройки будет show/hide settings
        self.toggle_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.start_button = tk.Button(self.master, text="Start", command=self.start_timer, font=("Helvetica", 14))
        self.start_button.grid(row=4, column=0, padx=20, pady=10)

        self.reset_button = tk.Button(self.master, text="Stop", command=self.reset_timer, font=("Helvetica", 14))
        self.reset_button.grid(row=4, column=1, padx=20, pady=10)

        self.settings_visible = True

        self.set_color("white")

    def select_all_text(self, event):
        event.widget.select_range(0, 'end')

    def set_color(self, color):
        self.label.config(fg=color)
        self.time_label.config(fg=color)

    def toggle_settings(self):
        if self.settings_visible:
            self.settings_frame.grid_remove()
            self.toggle_button.config(text="Show Settings")
        else:
            self.settings_frame.grid()
            self.toggle_button.config(text="Hide Settings")
        self.settings_visible = not self.settings_visible

    def update_times(self, event):
        try:
            work_minutes = int(self.work_time_entry.get())
            break_minutes = int(self.break_time_entry.get())
            self.work_time = work_minutes * 60
            self.break_time = break_minutes * 60
            self.reset_timer()
        except ValueError:
            pass

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def update_timer(self):
        if self.timer_running:
            if self.time_left > 0:
                self.time_left -= 1

                if self.is_working and self.time_left <= 0.1 * self.work_time:
                    self.set_color("red")
                else:
                    self.set_color("blue" if self.is_working else "green")

                self.time_label.config(text=self.format_time(self.time_left))
                self.master.after(1000, self.update_timer)
            else:
                play_sound()
                if self.is_working:
                    self.time_left = self.break_time
                    self.label.config(text="Break Time")
                    self.set_color("green")
                else:
                    self.time_left = self.work_time
                    self.label.config(text="Work Time")
                    self.set_color("blue")
                self.is_working = not self.is_working
                self.update_timer()

    def start_timer(self):
        if not self.timer_running:
            play_sound()
            self.timer_running = True
            self.update_timer()

    def reset_timer(self):
        self.timer_running = False
        self.is_working = True
        self.time_left = self.work_time
        self.label.config(text="Work Time")
        self.set_color("white")
        self.time_label.config(text=self.format_time(self.time_left))
        self.work_time_entry.delete(0, tk.END)
        self.work_time_entry.insert(0, str(self.work_time // 60))
        self.break_time_entry.delete(0, tk.END)
        self.break_time_entry.insert(0, str(self.break_time // 60))

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(master=root)
    root.mainloop()
