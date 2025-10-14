import csv
from datetime import datetime

class Logger:
    def __init__(self, filename="exam_log.csv"):
        self.filename = filename

    def log_event(self, event_type, details=""):
        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now(), event_type, details])
