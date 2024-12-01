import base64
import tkinter as tk
from io import BytesIO
from threading import Thread

from PIL import Image, ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from playsound import playsound

from counter.execrise import Exercise
from eyesdetection.FatigueDetection import FatigueDetection
from counter.program_controll import ProgramController


def hide_elements(elements):
    for element in elements:
        element.grid_forget()


class Counter:
    def __init__(self):
        self.window = tk.Tk()
        self.img_counter = 0
        self.exercise = Exercise().get_exercise()
        FatigueDetection.start_detection(self.update_fatigue_status)
        self.total_seconds = 0
        self.is_rest = True
        self.ui_elements = {
            "user_status": tk.Label(),
            "main_title": tk.Label(),
            "hour_label": tk.Label(),
            "hours_spinbox": tk.Spinbox(),
            "minute_label": tk.Label(),
            "minutes_spinbox": tk.Spinbox(),
            "rest_minute_label": tk.Label(),
            "rest_minutes_spinbox": tk.Spinbox(),
            "confirm_button": tk.Button(),
            "image_label": tk.Label(),
            "image_description": tk.Label(),
            "next_exercise_btn": tk.Button(self.window, text="Next Exercise", command=self.increment_img_counter),
            "exercise_img": tk.Label(),
            "show_stats_btn": tk.Button(),
            "time_label": tk.Label(),
            "back_btn": tk.Button(),
            "graph_canvas": None
        }

        self.window.title("Timer")
        self.window.geometry("500x580")
        self.window.configure(bg='#2c3e50')

        self.start_tracking()

        self.setup_ui()

    def start_tracking(self):
        tracking_thread = Thread(target=ProgramController.track_active_window, daemon=True)
        tracking_thread.start()

    def update_fatigue_status(self, status):
        if status == "Tired":
            self.ui_elements["user_status"].config(text="User is Tired!")
        elif status == "Not Tired":
            self.ui_elements["user_status"].config(text="User is Not Tired!")
        elif status == "Calibrating":
            self.ui_elements["user_status"].config(text="Calibrating...")
        self.ui_elements["user_status"].grid(row=0, column=4, columnspan=2, pady=10)



    def increment_img_counter(self):
        if self.img_counter >= len(self.exercise) - 1:
            self.img_counter = 0
        else:
            self.img_counter += 1
        self.show_current_exercise()

    def show_usage_graph(self):
        """Create and display the usage graph in the Tkinter window."""
        if not ProgramController.usage_log:
            print("No data available for graph.")
            return


        programs = list(ProgramController.usage_log.keys())
        usage_times = list(ProgramController.usage_log.values())


        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(programs, usage_times, color="skyblue")
        ax.set_xlabel("Time (seconds)", fontsize=12)
        ax.set_ylabel("Programs", fontsize=12)
        ax.set_title("Program Usage", fontsize=16)
        plt.tight_layout()


        if self.ui_elements["graph_canvas"] is not None:
            self.ui_elements["graph_canvas"].get_tk_widget().destroy()


        self.ui_elements["graph_canvas"] = FigureCanvasTkAgg(fig, master=self.window)
        self.ui_elements["graph_canvas"].draw()
        self.ui_elements["graph_canvas"].get_tk_widget().grid(row=5, column=0, columnspan=2, pady=10)


        plt.close(fig)

    def setup_ui(self):
        self.configure_grid()
        self.create_main_title()
        self.create_work_time_inputs()
        self.create_rest_time_inputs()
        self.create_buttons()
        self.show_work_time_inputs()

    def show_time_label(self):
        self.ui_elements["time_label"] = tk.Label(
            self.window, font=('Helvetica', 18, 'bold'), fg='white', bg='#2c3e50'
        )
        self.ui_elements["time_label"].grid(row=1, column=0, columnspan=2, pady=10)

    def configure_grid(self):
        for i in range(4):
            self.window.grid_rowconfigure(i, weight=1)
        for j in range(2):
            self.window.grid_columnconfigure(j, weight=1)

    def create_main_title(self):
        self.ui_elements["main_title"] = tk.Label(
            self.window, text="Specify the work time", font=('Helvetica', 18, 'bold'),
            fg='white', bg='#2c3e50'
        )
        self.ui_elements["main_title"].grid(row=0, column=0, columnspan=2, pady=10)

    def create_work_time_inputs(self):
        self.ui_elements["hour_label"] = tk.Label(self.window, text="Hours:", fg='white', bg='#2c3e50')
        self.ui_elements["hours_spinbox"] = tk.Spinbox(self.window, from_=0, to=23, width=5, font=('Helvetica', 12))
        self.ui_elements["minute_label"] = tk.Label(self.window, text="Minutes:", fg='white', bg='#2c3e50')
        self.ui_elements["minutes_spinbox"] = tk.Spinbox(self.window, from_=0, to=59, width=5, font=('Helvetica', 12))

    def show_work_time_inputs(self):
        self.ui_elements["hour_label"].grid(row=1, column=0, padx=10, pady=5)
        self.ui_elements["hours_spinbox"].grid(row=1, column=1, padx=10, pady=5)
        self.ui_elements["minute_label"].grid(row=2, column=0, padx=10, pady=5)
        self.ui_elements["minutes_spinbox"].grid(row=2, column=1, padx=10, pady=5)

    def create_rest_time_inputs(self):
        self.ui_elements["rest_minute_label"] = tk.Label(self.window, text="Rest Minutes:", fg='white', bg='#2c3e50')
        self.ui_elements["rest_minutes_spinbox"] = tk.Spinbox(self.window, from_=0, to=59, width=5,
                                                              font=('Helvetica', 12))

    def show_rest_time_inputs(self):
        hide_elements(
            [self.ui_elements["hour_label"], self.ui_elements["hours_spinbox"], self.ui_elements["minute_label"],
             self.ui_elements["minutes_spinbox"], self.ui_elements["confirm_button"]])
        self.ui_elements["main_title"].config(text="Specify the rest time")
        self.ui_elements["rest_minute_label"].grid(row=1, column=0, padx=10, pady=5)
        self.ui_elements["rest_minutes_spinbox"].grid(row=1, column=1, padx=10, pady=5)
        self.ui_elements["rest_confirm_button"].grid(row=2, column=0, columnspan=2, pady=10)

    def create_buttons(self):
        self.ui_elements["confirm_button"] = tk.Button(
            self.window, text="Confirm", command=self.show_rest_time_inputs,
            font=('Helvetica', 12, 'bold'), bg='#e74c3c', fg='black'
        )
        self.ui_elements["confirm_button"].grid(row=3, column=0, columnspan=2, pady=10)

        self.ui_elements["rest_confirm_button"] = tk.Button(
            self.window, text="Start Timer", command=self.start_timer,
            font=('Helvetica', 12, 'bold'), bg='#1abc9c', fg='black'
        )

    def start_timer(self):
        """Start the work timer."""
        hide_elements([
            self.ui_elements["image_label"],
            self.ui_elements["image_description"],
            self.ui_elements["next_exercise_btn"],
            self.ui_elements["rest_minutes_spinbox"],
            self.ui_elements["rest_minute_label"],
            self.ui_elements["rest_confirm_button"],
            self.ui_elements["exercise_img"],
        ])
        self.ui_elements["main_title"].config(text="Work Timer Started!")


        if not self.is_rest:
            hours = int(self.ui_elements["hours_spinbox"].get())
            minutes = int(self.ui_elements["minutes_spinbox"].get())
            self.total_seconds = hours * 3600 + minutes * 60

        self.show_time_label()
        self.countdown()

    def countdown(self):
        """Handle countdown logic for both work and rest phases."""
        self.total_seconds -= 1
        if self.total_seconds > 0:
            hrs, secs = divmod(self.total_seconds, 3600)
            mins, secs = divmod(secs, 60)
            self.ui_elements["time_label"].config(text=f"{hrs:02}:{mins:02}:{secs:02}")
            self.window.after(1000, self.countdown)
        else:
            if self.is_rest:
                hide_elements([
                    self.ui_elements["image_label"],
                    self.ui_elements["image_description"],
                    self.ui_elements["next_exercise_btn"],
                    self.ui_elements["rest_minutes_spinbox"],
                    self.ui_elements["rest_minute_label"],
                    self.ui_elements["rest_confirm_button"],
                    self.ui_elements["exercise_img"]
                ])
                self.is_rest = False
                playsound('sounds/work.mp3')
                self.ui_elements["main_title"].config(text="Work Timer Restarted!")
                self.start_timer()
            else:

                self.is_rest = True
                playsound('sounds/rest.mp3')
                self.ui_elements["main_title"].config(text="Rest Time!")
                minutes = int(self.ui_elements["rest_minutes_spinbox"].get())
                self.total_seconds = minutes * 60
                self.show_current_exercise()
                self.countdown()

    def show_statistics(self):
        hide_elements([
            self.ui_elements["image_label"],
            self.ui_elements["exercise_img"],
            self.ui_elements["image_description"],
            self.ui_elements["next_exercise_btn"],
            self.ui_elements["rest_minutes_spinbox"],
            self.ui_elements["rest_minute_label"],
            self.ui_elements["rest_confirm_button"],
            self.ui_elements["main_title"],
            self.ui_elements["hour_label"],
            self.ui_elements["minute_label"],
            self.ui_elements["time_label"],
            self.ui_elements["show_stats_btn"]
        ])

        self.ui_elements["back_btn"] = tk.Button()

        self.ui_elements["back_btn"].config(text="Back", command=self.exercise_back)
        self.ui_elements["back_btn"].grid(row=3, column=0, columnspan=2, pady=10)
        self.show_usage_graph()

    def exercise_back(self):
        if self.ui_elements["graph_canvas"] is not None:
            self.ui_elements["graph_canvas"].get_tk_widget().destroy()
            self.ui_elements["graph_canvas"] = None
        hide_elements([self.ui_elements["back_btn"]])
        self.create_main_title()
        if self.is_rest:
            self.ui_elements["main_title"].config(text="Rest Time!")
            self.show_exercise_control_elements()
        else:
            self.ui_elements["main_title"].config(text="Work Time!")
        self.show_time_label()

    def show_current_exercise(self):
        self.exercise = Exercise().get_exercise()
        if self.ui_elements["exercise_img"] is not None:
            self.ui_elements["exercise_img"].grid_forget()
            self.ui_elements["exercise_img"] = None
        cur_exercise = self.exercise[self.img_counter]
        base64_data = cur_exercise["image"]

        try:
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            window_width = self.window.winfo_width()
            window_height = self.window.winfo_height()

            self.ui_elements["image_label"].config(
                text=cur_exercise["name"],
                bg=self.window["bg"],
                fg="white",
                font=("Arial", 12),
                justify="left")
            self.ui_elements["image_label"].grid(row=3, column=0, columnspan=2, pady=10)

            self.ui_elements["image_description"].config(
                text=cur_exercise["description"],
                wraplength=int(window_width * 0.8),
                bg=self.window["bg"],
                fg="white",
                font=("Arial", 12),
                justify="left"
            )
            self.ui_elements["image_description"].grid(row=4, column=0, columnspan=2, pady=10)

            new_width = int(window_width * 0.6)
            new_height = int(window_height * 0.6)

            resized_image = image.resize((new_width, new_height), Image.ADAPTIVE)
            photo = ImageTk.PhotoImage(resized_image)
            self.ui_elements["exercise_img"] = tk.Label(self.window, image=photo)
            self.ui_elements["exercise_img"].image = photo
            self.show_exercise_control_elements()
        except Exception as e:
            print(f"Error opening or displaying the image: {e}")

    def show_exercise_control_elements(self):
        self.ui_elements["exercise_img"].grid(row=5, column=0, columnspan=2, pady=10)
        self.ui_elements["next_exercise_btn"].grid(row=6, column=0, columnspan=2, pady=10)
        self.ui_elements["show_stats_btn"].config(text="Show Statistics", command=self.show_statistics)
        self.ui_elements["show_stats_btn"].grid(row=7, column=0, columnspan=2, pady=10)

    def run(self):
        self.window.mainloop()
