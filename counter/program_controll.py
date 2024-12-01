import time
from threading import Thread, Event
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGWindowListExcludeDesktopElements,
)
from AppKit import NSWorkspace
from collections import defaultdict


class ProgramController:
    usage_log = defaultdict(float)
    active_window = None
    start_time = None
    stop_event = Event()

    @staticmethod
    def get_active_window():
        """Get the full title of the currently active window."""
        try:

            active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            app_name = active_app.localizedName()


            windows = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements, 0
            )
            for window in windows:
                if (
                    "kCGWindowOwnerName" in window
                    and window["kCGWindowOwnerName"] == app_name
                    and "kCGWindowName" in window
                ):

                    return f"{app_name} - {window['kCGWindowName']}"
            return app_name
        except Exception as e:
            print(f"Error getting active window: {e}")
            return "Unknown Window"

    @staticmethod
    def track_active_window():
        """Track time spent on each active window."""
        print("Tracking started.")
        ProgramController.start_time = time.time()
        while not ProgramController.stop_event.is_set():
            current_window = ProgramController.get_active_window()
            current_time = time.time()

            if current_window != ProgramController.active_window:
                if ProgramController.active_window:
                    elapsed_time = current_time - ProgramController.start_time
                    ProgramController.usage_log[ProgramController.active_window] += elapsed_time
                    print(f"Switched from '{ProgramController.active_window}' after {elapsed_time:.2f} seconds.")

                ProgramController.active_window = current_window
                ProgramController.start_time = current_time
                print(f"Now active: {ProgramController.active_window}")

            time.sleep(1)

    @staticmethod
    def stop_tracking():
        """Stop tracking active windows."""
        ProgramController.stop_event.set()
        print("\nTracking stopped.")

    @staticmethod
    def print_usage_summary():
        """Print a summary of time spent on each window."""
        if not ProgramController.usage_log:
            print("\nNo data to display.")
            return
        print("\nTime Spent on Programs:")
        for window, seconds in ProgramController.usage_log.items():
            print(f"{window}: {seconds:.2f} seconds")
