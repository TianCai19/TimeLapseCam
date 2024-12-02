
import cv2
import time
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QSlider, QPushButton, QColorDialog, QFileDialog, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import sys
from study_time_manager import StudyTimeManager

class TimeLapseCam(QWidget):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.init_ui()
        self.setup_directories()
        self.setup_camera()
        self.start_time = time.time()
        self.study_time_manager = StudyTimeManager()  # 初始化学习时间管理器
        self.study_time = self.study_time_manager.get_today_study_time()  # 获取今日学习时间

        self.capturing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_frame)

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

    def init_ui(self):
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
        self.fps_slider.setMaximum(30)  # 支持 1 到 30 帧
        self.fps_slider.setValue(2)  # 默认帧率 2 (每帧 0.5 秒)
        fps_layout.addWidget(fps_label)
        fps_layout.addWidget(self.fps_slider)
        layout.addLayout(fps_layout)
        
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

        self.setLayout(layout)

    def setup_directories(self):
        # Create directories if they don't exist
        os.makedirs('frames', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        os.makedirs(os.path.dirname(self.config["font_path"]), exist_ok=True)

    def setup_camera(self):
        # Initialize OpenCV camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_label.setText("Status: Cannot access camera")
            self.start_button.setEnabled(False)
        else:
            self.status_label.setText("Status: Camera Ready")

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
        else:
            self.capturing = False
            self.start_button.setText("Start Capturing")
            self.status_label.setText("Status: Idle")
            self.timer.stop()

    def save_settings(self):
        self.save_config()
        self.status_label.setText("Status: Settings Saved")

    def capture_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            # Overlay text
            overlaid_image = self.overlay_text(pil_image)

            # Save frame
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            frame_filename = f"frames/frame_{timestamp}.png"
            overlaid_image.save(frame_filename)

            # Update study time
            self.study_time += self.config["capture_interval"]
            
            self.study_time_manager.add_study_time(self.config["capture_interval"])  # 保存到文件
            self.status_label.setText(f"Status: Captured {frame_filename}. Study Time: {self.study_time} seconds")
        else:
            self.status_label.setText("Status: Failed to capture frame")

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

        return image

    def compile_video(self):
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

    def closeEvent(self, event):
        # Release camera and compile video on exit
        if self.cap.isOpened():
            self.cap.release()
        self.compile_video()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = TimeLapseCam()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()