import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import cv2
import time
import os
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QSlider, QPushButton, QColorDialog, QFileDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QTextEdit, QCalendarWidget, QDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import sys
from study_time_manager import StudyTimeManager
from task_manager import TaskManager

class DateSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择日期")
        layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

class TimeLapseCam(QWidget):
    """
    Main application window for TimeLapseCam.
    Handles UI interactions, camera operations, and video compilation.
    """

    def __init__(self) -> None:
        super().__init__()
        self.load_config()
        self.task_manager = TaskManager(task_file="tasks.json", log_file="task_log.json")
        self.init_ui()
        self.setup_directories()
        self.setup_camera()

        self.start_time = time.time()
        self.study_time_manager = StudyTimeManager()
        self.study_time = self.study_time_manager.get_today_study_time()

        self.capturing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_frame)
        self.date_str = datetime.now().strftime('%Y-%m-%d')

    def load_config(self):
        # Load configuration from config.json
        default_config = {
            "text_size": 20,
            "text_color": "#FFFFFF",
            "capture_interval": 5,
            "font_path": "assets/fonts/Arial.ttf"
            
        }
        if not os.path.exists('config.json'):
            with open('config.json', 'w') as f:
                json.dump(default_config, f, indent=4)
            self.config = default_config
        else:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        # Ensure font path exists
        if not os.path.exists(self.config["font_path"]):
            self.config["font_path"] = "assets/fonts/Arial.ttf"  # fallback to default
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4)

    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)

    def init_ui(self) -> None:
        """
        Initialize the user interface components.
        """
        try:
            self.setWindowTitle("TimeLapseCam")
            self.setGeometry(100, 100, 400, 300)

            layout = QVBoxLayout()

            # Text Size Slider
            text_size_layout = QHBoxLayout()
            text_size_label = QLabel("Text Size:")
            self.text_size_slider = QSlider(Qt.Horizontal)
            self.text_size_slider.setMinimum(10)
            self.text_size_slider.setMaximum(50)
            self.text_size_slider.setValue(self.config["text_size"])
            self.text_size_slider.valueChanged.connect(self.update_text_size)
            text_size_layout.addWidget(text_size_label)
            text_size_layout.addWidget(self.text_size_slider)
            layout.addLayout(text_size_layout)

            # Text Color Picker
            text_color_layout = QHBoxLayout()
            text_color_label = QLabel("Text Color:")
            self.text_color_button = QPushButton()
            self.text_color_button.setStyleSheet(f"background-color: {self.config['text_color']}")
            self.text_color_button.clicked.connect(self.choose_text_color)
            text_color_layout.addWidget(text_color_label)
            text_color_layout.addWidget(self.text_color_button)
            layout.addLayout(text_color_layout)

            # Capture Interval Slider
            capture_interval_layout = QHBoxLayout()
            capture_interval_label = QLabel("Capture Interval (s):")
            self.capture_interval_slider = QSlider(Qt.Horizontal)
            self.capture_interval_slider.setMinimum(1)
            self.capture_interval_slider.setMaximum(60)
            self.capture_interval_slider.setValue(self.config["capture_interval"])
            self.capture_interval_slider.valueChanged.connect(self.update_capture_interval)
            capture_interval_layout.addWidget(capture_interval_label)
            capture_interval_layout.addWidget(self.capture_interval_slider)
            layout.addLayout(capture_interval_layout)

            # FPS Slider
            fps_layout = QHBoxLayout()
            fps_label = QLabel("Frames per Second (FPS):")
            self.fps_slider = QSlider(Qt.Horizontal)
            self.fps_slider.setMinimum(1)
            self.fps_slider.setMaximum(60)  # 支持 1 到 30 帧
            self.fps_slider.setValue(2)  # 默认帧率 2 (每帧 0.5 秒)
            # 显示当前帧率
            self.fps_value_label = QLabel(str(self.fps_slider.value()))  # 显示当前帧率值
            
            # read from config
            self.fps_slider.setValue(self.config.get("fps", 2))
            fps_layout.addWidget(fps_label)
            fps_layout.addWidget(self.fps_slider)
            layout.addLayout(fps_layout)
            
            # Task Dropdown
            task_dropdown_layout = QHBoxLayout()
            task_label = QLabel("Select Task:")
            self.task_dropdown = QComboBox()
            tasks = self.task_manager.get_all_tasks()  # 获取任务列表
            self.task_dropdown.addItems(tasks)  # 加载已有任务
            self.task_dropdown.currentTextChanged.connect(self.select_task)
            task_dropdown_layout.addWidget(task_label)
            task_dropdown_layout.addWidget(self.task_dropdown)
            layout.addLayout(task_dropdown_layout)

            
            # Set default task if no task is selected
            if tasks:
                default_task = tasks[0]
                self.task_manager.start_task(default_task)
                self.task_dropdown.setCurrentText(default_task)
                logging.info(f"Default task selected: {default_task}")
                #��里会输出到终端吗？logging.info(f"Default task selected: {default_task}")
                #答案：

            # New Task Input
            new_task_layout = QHBoxLayout()
            new_task_label = QLabel("New Task:")
            self.new_task_input = QLineEdit()
            self.new_task_input.setPlaceholderText("Enter a new task...")
            new_task_button = QPushButton("Add Task")
            new_task_button.clicked.connect(self.add_task)
            new_task_layout.addWidget(new_task_label)
            new_task_layout.addWidget(self.new_task_input)
            new_task_layout.addWidget(new_task_button)
            layout.addLayout(new_task_layout)
            
            # Start/Stop Button
            self.start_button = QPushButton("Start Capturing")
            self.start_button.clicked.connect(self.toggle_capturing)
            layout.addWidget(self.start_button)

            # Status Label
            self.status_label = QLabel("Status: Idle")
            layout.addWidget(self.status_label)

            # Save and Exit Button
            save_exit_layout = QHBoxLayout()
            self.save_button = QPushButton("Save Settings")
            self.save_button.clicked.connect(self.save_settings)
            self.exit_button = QPushButton("Exit")
            self.exit_button.clicked.connect(self.close)
            save_exit_layout.addWidget(self.save_button)
            save_exit_layout.addWidget(self.exit_button)
            layout.addLayout(save_exit_layout)

            # 日志按钮
            log_button = QPushButton("Show Daily Log")
            log_button.clicked.connect(self.show_daily_log)
            layout.addWidget(log_button)

            # 在保存和退出按钮之前添加生成视频按钮
            generate_video_layout = QHBoxLayout()
            self.generate_video_button = QPushButton("生成视频")
            self.generate_video_button.clicked.connect(self.show_generate_video_dialog)
            generate_video_layout.addWidget(self.generate_video_button)
            layout.addLayout(generate_video_layout)

            # 视频生成按钮组
            video_buttons_layout = QHBoxLayout()
            
            # 生成今日视频按钮
            self.generate_today_video_button = QPushButton("生成今日视频")
            self.generate_today_video_button.clicked.connect(self.generate_today_video)
            
            # 选择日期生成视频按钮
            self.generate_video_button = QPushButton("选择日期生成视频")
            self.generate_video_button.clicked.connect(self.show_generate_video_dialog)
            
            video_buttons_layout.addWidget(self.generate_today_video_button)
            video_buttons_layout.addWidget(self.generate_video_button)
            layout.addLayout(video_buttons_layout)

            self.setLayout(layout)
            logging.info("UI initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing UI: {e}")
            self.status_label.setText("Status: UI Initialization Failed")

    def select_task(self, task_name):
        """
        选择任务
        """
        self.task_manager.start_task(task_name)
        #log out the task choose
        logging.info(f"Task selected: {task_name}")

    def add_task(self):
        """
        添加新任务
        """
        task_name = self.new_task_input.text()
        if task_name and task_name not in self.task_manager.get_all_tasks():
            self.task_manager.start_task(task_name)
            self.task_dropdown.addItem(task_name)
            self.new_task_input.clear()
            logging.info(f"New task added: {task_name}")

    def setup_directories(self):
        # Create directories if they don't exist
        os.makedirs('frames', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        os.makedirs(os.path.dirname(self.config["font_path"]), exist_ok=True)
        self.date_str = datetime.now().strftime('%Y-%m-%d')
        self.frames_dir = os.path.join('frames', self.date_str)
        os.makedirs(self.frames_dir, exist_ok=True)
        self.output_dir = 'output'
        os.makedirs(self.output_dir, exist_ok=True)

    def setup_camera(self) -> None:
        """
        Initialize the camera for capturing frames.
        """
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.status_label.setText("Status: Cannot access camera")
                self.start_button.setEnabled(False)
                logging.error("Camera could not be accessed.")
            else:
                self.status_label.setText("Status: Camera Ready")
                logging.info("Camera initialized successfully.")
        except Exception as e:
            logging.exception("Exception occurred while setting up the camera.")
            self.status_label.setText("Status: Camera Setup Failed")

    def update_text_size(self, value):
        self.config["text_size"] = value

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.config["text_color"] = color.name()
            self.text_color_button.setStyleSheet(f"background-color: {self.config['text_color']}")

    def update_capture_interval(self, value):
        self.config["capture_interval"] = value
        if self.capturing:
            self.timer.stop()
            self.timer.start(self.config["capture_interval"] * 1000)

    def toggle_capturing(self):
        if not self.capturing:
            self.capturing = True
            self.start_button.setText("Stop Capturing")
            self.status_label.setText("Status: Capturing")
            self.timer.start(self.config["capture_interval"] * 1000)
            logging.info("Started capturing")
        else:
            self.capturing = False
            self.start_button.setText("Start Capturing")
            self.status_label.setText("Status: Idle")
            self.timer.stop()
            logging.info("Stopped capturing")

    def save_settings(self):
        self.save_config()
        self.status_label.setText("Status: Settings Saved")

    target_size = (1920, 1080)  # 目标分辨率

    def capture_frame(self) -> None:
        """
        Capture a frame from the camera, process it, and save.
        """
        try:
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)

                # Resize image to target size
                if pil_image.size != self.target_size:
                    pil_image = pil_image.resize(self.target_size, Image.LANCZOS)

                # Overlay text
                overlaid_image = self.overlay_text(pil_image)

                # Save frame
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                frame_filename = os.path.join(self.frames_dir, f"frame_{timestamp}.png")
                overlaid_image.save(frame_filename)

                # Update study time
                self.study_time += self.config["capture_interval"]
                self.study_time_manager.add_study_time(self.config["capture_interval"])  # 保存到文件
                self.status_label.setText(f"Status: Captured {frame_filename}. Study Time: {self.study_time} seconds")
                logging.debug(f"Captured frame: {frame_filename}")
            else:
                self.status_label.setText("Status: Failed to capture frame")
                logging.error("Failed to capture frame")
        except Exception as e:
            logging.exception("Exception occurred during frame capture.")
            self.status_label.setText("Status: Error during frame capture")

    def overlay_text(self, image):
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self.config["font_path"], self.config["text_size"])

        # Current Time
        current_time = datetime.now().strftime("%H:%M:%S")
        draw.text((10, 10), f"Current Time: {current_time}", fill=self.config["text_color"], font=font)

        # Study Time
        hours, remainder = divmod(int(self.study_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        study_time_str = f"Study Time: {hours:02d}:{minutes:02d}:{seconds:02d}"
        draw.text((10, 10 + self.config["text_size"] + 5), study_time_str, fill=self.config["text_color"], font=font)
        
        # current task time
        task_name = self.task_manager.current_task
        if task_name:
            #task_time = self.task_manager.get_task_time(task_name)
            #hours, remainder = divmod(task_time, 3600)
            #minutes, seconds = divmod(remainder, 60)
            task_time_str = f"Task: {task_name} "
            draw.text((10, 10 + 2 * (self.config["text_size"] + 5)), task_time_str, fill=self.config["text_color"], font=font)

        # 叠加学习总时间
        study_time = self.study_time_manager.get_today_study_time()
        hours, remainder = divmod(int(study_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        study_time_str = f"Total Study Time: {hours:02d}:{minutes:02d}:{seconds:02d}"
        draw.text(
            (10, 10 + 3 * (self.config["text_size"] + 5)),
            study_time_str,
            fill=self.config["text_color"],
            font=font
        )

        return image

    def compile_video(self) -> None:
        """
        Compile captured frames into a time-lapse video.
        """
        try:
            frames_dir = 'frames'
            output_dir = 'output'
            output_filename = f"{output_dir}/timelapse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

            # Get list of frame files
            frame_files = sorted(
                [os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.png')]
            )

            if not frame_files:
                self.status_label.setText("Status: No frames to compile")
                return
                    # 从滑块读取 FPS
            fps = self.fps_slider.value()  # 用户通过 GUI 滑块选择帧率
        # Create the video using MoviePy
            try:
                clip = ImageSequenceClip(frame_files, fps=fps)
                clip.write_videofile(output_filename, codec='libx264')
                print(f"Timelapse video saved at {output_filename}")
            except Exception as e:
                print(f"Error creating video: {e}")

            self.status_label.setText(f"Status: Video saved to {output_filename}")
            date_folders = [d for d in os.listdir('frames') if os.path.isdir(os.path.join('frames', d))]
            for date_str in date_folders:
                frames_dir = os.path.join('frames', date_str)
                output_filename = os.path.join(self.output_dir, f"timelapse_{date_str}.mp4")
                frame_files = sorted(
                    [os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.png')]
                )
                if not frame_files:
                    continue
                fps = self.fps_slider.value()
                try:
                    clip = ImageSequenceClip(frame_files, fps=fps)
                    clip.write_videofile(output_filename, codec='libx264')
                except Exception as e:
                    print(f"Error creating video for {date_str}: {e}")
            self.status_label.setText("Status: Videos compiled")
            logging.info(f"Video compiled successfully: {output_filename}")
        except Exception as e:
            logging.exception("Exception occurred during video compilation.")
            self.status_label.setText("Status: Error creating video")

    def show_generate_video_dialog(self):
        dialog = DateSelectorDialog(self)
        if (dialog.exec_() == QDialog.Accepted):
            selected_date = dialog.calendar.selectedDate()
            date_str = selected_date.toString('yyyy-MM-dd')
            self.generate_video_for_date(date_str)

    def generate_video_for_date(self, date_str):
        frames_dir = os.path.join('frames', date_str)
        if not os.path.exists(frames_dir):
            self.status_label.setText(f"Status: No frames found for {date_str}")
            logging.warning(f"No frames found for {date_str}")
            return

        output_filename = os.path.join(self.output_dir, f"timelapse_{date_str}.mp4")
        frame_files = sorted(
            [os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.png')]
        )
        
        if not frame_files:
            self.status_label.setText(f"Status: No frames found for {date_str}")
            logging.warning(f"No frames found for {date_str}")
            return

        fps = self.fps_slider.value()
        try:
            clip = ImageSequenceClip(frame_files, fps=fps)
            clip.write_videofile(output_filename, codec='libx264')
            self.status_label.setText(f"Status: Video saved to {output_filename}")
            logging.info(f"Video saved to {output_filename}")
        except Exception as e:
            self.status_label.setText(f"Status: Error creating video - {str(e)}")
            logging.error(f"Error creating video for {date_str}: {e}")

    def generate_today_video(self):
        """
        生成今天的视频
        """
        today_str = datetime.now().strftime('%Y-%m-%d')
        self.generate_video_for_date(today_str)

    def show_daily_log(self):
        """
        显示每日任务日志和学习记录
        """
        # 获取当日任务日志
        daily_log = self.task_manager.get_daily_log()
        # 获取当日学习时间
        study_time = self.study_time_manager.get_today_study_time()
        # 格式化日志内容
        log_text = f"Date: {self.date_str}\n\nTasks:\n"
        for record in daily_log:
            task_name = record["task_name"]
            start_time = record["start_time"]
            end_time = record["end_time"] or "In Progress"
            log_text += f"- {task_name}: {start_time} - {end_time}\n"
        hours, remainder = divmod(int(study_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        study_time_str = f"\nTotal Study Time: {hours:02d}:{minutes:02d}:{seconds:02d}"
        log_text += study_time_str
        # 显示日志窗口
        self.log_window = QWidget()
        self.log_window.setWindowTitle("Daily Log")
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(log_text)
        layout.addWidget(text_edit)
        self.log_window.setLayout(layout)
        self.log_window.show()

    def closeEvent(self, event) -> None:
        """
        Handle the application close event.
        """
        try:
            self.task_manager.end_current_task()
            if self.cap.isOpened():
                self.cap.release()
            logging.info("Application closed")
            event.accept()
        except Exception as e:
            logging.exception("Exception occurred during application close.")
            event.accept()

def main():
    app = QApplication(sys.argv)
    window = TimeLapseCam()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()