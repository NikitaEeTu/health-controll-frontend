import matplotlib.pyplot as plt
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class UsageGraph:
    def __init__(self, usage_data, master_window):
        """
        Initialize the UsageGraph class.

        :param usage_data: Dictionary of program names and their usage times.
        :param master_window: The main Tkinter window instance.
        """
        self.usage_data = usage_data
        self.master_window = master_window

    def create_graph(self):
        """Create the graph using matplotlib."""
        if not self.usage_data:
            print("No data available for graph.")
            return None

        programs = list(self.usage_data.keys())
        usage_times = list(self.usage_data.values())


        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(programs, usage_times, color="skyblue")
        ax.set_xlabel("Time (seconds)", fontsize=12)
        ax.set_ylabel("Programs", fontsize=12)
        ax.set_title("Program Usage", fontsize=16)
        plt.tight_layout()
        return fig

    def show_graph(self):
        """Display the graph in a new Tkinter window."""
        fig = self.create_graph()
        if fig is None:
            return


        new_window = Toplevel(self.master_window)
        new_window.title("Program Usage Graph")
        new_window.geometry("800x600")


        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


        plt.close(fig)
