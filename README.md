# TimeLapseCam

A Python application for time-lapse photography on macOS. It captures frames from the Mac's camera at set intervals, overlays the current time and studying time, and compiles the frames into a time-lapse video. Users can customize text size and color through a graphical interface.

## Features

- Access Mac's camera to capture frames at user-defined intervals.
- Overlay current time and total study time on each frame.
- Customize text size and color.
- Save captured frames locally.
- Compile frames into a time-lapse video.

## Requirements

- Python 3.7+
- Listed in `requirements.txt`

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/TimeLapseCam.git
    cd TimeLapseCam
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure `config.json` is properly configured.

4. Place desired `.ttf` font files in `assets/fonts/`.

## Usage

Run the application:
```bash
python main.py