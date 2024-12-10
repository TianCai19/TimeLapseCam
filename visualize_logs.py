import json
import os
from datetime import datetime

class LogVisualizer:
    def __init__(self, log_file="task_log.json"):
        self.log_file = log_file
        self.load_logs()

    def load_logs(self):
        if not os.path.exists(self.log_file):
            print("Log file does not exist.")
            self.logs = {}
            return
        with open(self.log_file, "r") as f:
            self.logs = json.load(f)

    def visualize_daily_study_time(self, date_str):
        if date_str not in self.logs:
            print(f"No logs found for {date_str}.")
            return
        tasks = self.logs[date_str]
        task_times = {}
        for task in tasks:
            if task["end_time"]:
                start = datetime.strptime(task["start_time"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(task["end_time"], "%Y-%m-%d %H:%M:%S")
                duration = (end - start).total_seconds() / 3600  # in hours
                task_times[task["task_name"]] = task_times.get(task["task_name"], 0) + duration
        if not task_times:
            print(f"No completed tasks for {date_str}.")
            return
        # Plotting
        tasks = list(task_times.keys())
        hours = list(task_times.values())
        plt.figure(figsize=(10, 6))
        plt.bar(tasks, hours, color='skyblue')
        plt.xlabel('Tasks')
        plt.ylabel('Hours Spent')
        plt.title(f'Study Time for {date_str}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def get_daily_data(self, date_str):
        if date_str not in self.logs:
            print(f"No logs found for {date_str}.")
            return {}
        tasks = self.logs[date_str]
        task_times = {}
        for task in tasks:
            if task["end_time"]:
                start = datetime.strptime(task["start_time"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(task["end_time"], "%Y-%m-%d %H:%M:%S")
                duration = (end - start).total_seconds() / 3600  # in hours
                task_times[task["task_name"]] = task_times.get(task["task_name"], 0) + duration
        return task_times

if __name__ == "__main__":
    visualizer = LogVisualizer()
    date = input("Enter date (YYYY-MM-DD): ")
    visualizer.visualize_daily_study_time(date)