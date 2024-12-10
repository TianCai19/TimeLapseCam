from datetime import datetime, timedelta
import json
import os

class TaskManager:
    def __init__(self, task_file="tasks.json", log_file="task_log.json"):
        """
        初始化任务管理器
        Args:
            task_file (str): 任务累计时间数据存储文件路径
            log_file (str): 任务日志数据存储文件路径
        """
        self.task_file = task_file
        self.log_file = log_file
        self.tasks = self.load_tasks()
        self.current_task = None
        self.task_start_time = None
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.task_log = self.load_task_log()

    def load_tasks(self):
        """
        从文件加载任务累计时间数据
        Returns:
            dict: 任务数据 {task_name: total_seconds}
        """
        if not os.path.exists(self.task_file):
            with open(self.task_file, "w") as f:
                json.dump({}, f)
                
        with open(self.task_file, "r") as f:
            return json.load(f)

    def load_task_log(self):
        """
        加载任务日志
        Returns:
            dict: 任务日志 {date: [{task_name, start_time, end_time}]}
        """
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump({}, f)
                
        with open(self.log_file, "r") as f:
            return json.load(f)

    def save_tasks(self):
        """
        保存任务累计时间数据到文件
        """
        with open(self.task_file, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def save_task_log(self):
        """
        保存任务日志到文件
        """
        with open(self.log_file, "w") as f:
            json.dump(self.task_log, f, indent=4)

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

        self.task_start_time = datetime.now()
        self.current_task = task_name
        # 确保当日的任务列表存在
        if self.date_str not in self.task_log:
            self.task_log[self.date_str] = []
        # 记录任务开始
        self.task_log[self.date_str].append({
            "task_name": task_name,
            "start_time": self.task_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None
        })

    def end_current_task(self):
        """
        结束当前任务并统计时间
        """
        if not self.current_task or not self.task_start_time:
            return

        # 计算经过的时间
        end_time = datetime.now()
        elapsed_time = (end_time - self.task_start_time).total_seconds()
        
        # 更新累计时间
        self.tasks[self.current_task] += elapsed_time
        
        # 更新任务日志
        if self.date_str in self.task_log and self.task_log[self.date_str]:
            self.task_log[self.date_str][-1]["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存数据
        self.save_tasks()
        self.save_task_log()
        
        # 重置当前任务状态
        self.task_start_time = None
        self.current_task = None
        
        print(f"Task ended: {self.current_task}, time added: {elapsed_time} seconds")

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
        获取所有任务的名称列表
        Returns:
            list: 任务名称列表
        """
        tasks = set(self.tasks.keys())  # 包含来自 tasks.json 的任务名称
        for day_logs in self.task_log.values():
            for record in day_logs:
                tasks.add(record["task_name"])
        return list(tasks)

    def get_daily_work_timeline(self):
        """
        返回一天的任务时间线（需要从日志提取实现）
        Returns:
            list: 每个任务的开始和结束时间记录
        """
        # 假设有日志文件记录每个任务切换的时间，可在此实现更详细的时间线分析
        # Placeholder: 可扩展为从日志文件读取并分析
        return [{"task": task, "time": timedelta(seconds=time)} for task, time in self.tasks.items()]

    def get_daily_log(self, date_str=None):
        """
        获取指定日期的任务日志
        Args:
            date_str (str): 日期字符串，格式为 'YYYY-MM-DD'。默认为今天。
        Returns:
            list: 当日的任务记录列表
        """
        if date_str is None:
            date_str = self.date_str
        return self.task_log.get(date_str, [])