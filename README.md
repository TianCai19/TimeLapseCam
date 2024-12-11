# TimeLapseCam

A Python application for time-lapse photography on macOS and Windows. It captures frames from the camera at set intervals, overlays the current time and studying time, and compiles the frames into a time-lapse video. Users can customize text size and color through a graphical interface.

## Features

- Access the camera to capture frames at user-defined intervals.
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

## Packaging with PyInstaller

### macOS and Linux

1. Install PyInstaller if not already installed:
    ```bash
    pip install pyinstaller
    ```

2. Navigate to the project directory and run PyInstaller:
    ```bash
    pyinstaller --onefile --add-data "config.json:." --add-data "assets/fonts/:assets/fonts/" main.py
    ```

    - `--onefile` creates a single executable.
    - `--add-data` includes additional files and directories.

3. The executable will be generated in the `dist` folder.

### Windows

1. Install PyInstaller if not already installed:
    ```bash
    pip install pyinstaller
    ```

2. Navigate to the project directory and run PyInstaller with Windows-specific syntax:
    ```bash
    pyinstaller --onefile --add-data "config.json;." --add-data "assets/fonts/;assets/fonts/" main.py
    ```

    - Note the use of semicolons (`;`) instead of colons (`:`) to separate source and destination paths on Windows.

3. The executable will be generated in the `dist` folder.

## Usage

Run the application:
```bash
python main.py