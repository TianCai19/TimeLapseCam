from datetime import datetime, timedelta
import json
import os

class TaskManager:
    def __init__(self, task_file="tasks.json"):
        """
        初始化任务管理器
        Args:
            task_file (str): 任务数据存储文件路径
        """
        self.task_file = task_file
        self.tasks = self.load_tasks()
        self.current_task = None
        self.task_start_time = None

    def load_tasks(self):
        """
        从文件加载任务数据
        Returns:
            dict: 任务数据 {task_name: total_seconds}
        """
        if os.path.exists(self.task_file):
            with open(self.task_file, "r") as f:
                return json.load(f)
        return {}

    def save_tasks(self):
        """
        保存任务数据到文件
        """
        with open(self.task_file, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def start_task(self, task_name):
        """
        开始一个任务
        Args:
            task_name (str): 任务名称
        """
        if self.current_task:
            self.end_current_task()  # 结束当前任务

        self.current_task = task_name
        self.task_start_time = datetime.now()
        if task_name not in self.tasks:
            self.tasks[task_name] = 0  # 初始化任务累计时间
        print(f"Task started: {task_name}")

    def end_current_task(self):
        """
        结束当前任务并统计时间
        """
        if not self.current_task or not self.task_start_time:
            return

        elapsed_time = (datetime.now() - self.task_start_time).total_seconds()
        self.tasks[self.current_task] += elapsed_time
        self.task_start_time = None
        print(f"Task ended: {self.current_task}, time added: {elapsed_time} seconds")

        self.save_tasks()
        self.current_task = None

    def get_task_time(self, task_name):
        """
        获取某任务的累计时间
        Args:
            task_name (str): 任务名称
        Returns:
            int: 累计时间（秒）
        """
        return self.tasks.get(task_name, 0)

    def get_all_tasks(self):
        """
        获取所有任务的名称及时间
        Returns:
            dict: {task_name: total_seconds}
        """
        return self.tasks

    def get_daily_work_timeline(self):
        """
        返回一天的任务时间线（需要从日志提取实现）
        Returns:
            list: 每个任务的开始和结束时间记录
        """
        # 假设有日志文件记录每个任务切换的时间，可在此实现更详细的时间线分析
        # Placeholder: 可扩展为从日志文件读取并分析
        return [{"task": task, "time": timedelta(seconds=time)} for task, time in self.tasks.items()]