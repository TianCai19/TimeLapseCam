import json
import os
from datetime import datetime

class StudyTimeManager:
    def __init__(self, file_path="study_time.json"):
        """
        初始化学习时间管理器
        Args:
            file_path (str): 存储学习时间的文件路径
        """
        self.file_path = file_path
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data = self.load_study_time()

    def load_study_time(self):
        """
        加载学习时间数据
        Returns:
            dict: 学习时间数据（以日期为键）
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {}

    def save_study_time(self):
        """
        将学习时间数据保存到文件
        """
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_today_study_time(self):
        """
        获取今日的学习时间
        Returns:
            int: 今日学习时间（秒）
        """
        return self.data.get(self.today, 0)

    def add_study_time(self, seconds):
        """
        增加今日的学习时间
        Args:
            seconds (int): 增加的时间（秒）
        """
        self.data[self.today] = self.get_today_study_time() + seconds
        self.save_study_time()

    def get_all_study_times(self):
        """
        获取所有学习时间数据
        Returns:
            dict: 所有学习时间数据（以日期为键）
        """
        return self.data