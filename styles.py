def get_main_style():
    return """
        QWidget {
            background-color: #f0f0f0;
            font-family: Arial;
        }
        
        QLabel {
            color: #2c3e50;
            font-size: 14px;
            padding: 5px;
        }
        
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-size: 14px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QPushButton:pressed {
            background-color: #2574a9;
        }
        
        QSlider {
            height: 25px;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #bdc3c7;
            height: 5px;
            background: #e0e0e0;
            margin: 0px;
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background: #3498db;
            border: none;
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }
        
        QComboBox {
            padding: 5px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            background: white;
        }
        
        QLineEdit {
            padding: 5px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            background: white;
        }
        
        QTextEdit {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            background: white;
            padding: 5px;
        }
    """

def get_start_button_style():
    return """
        QPushButton {
            background-color: #27ae60;
            font-weight: bold;
            padding: 10px 20px;
        }
        QPushButton:hover {
            background-color: #219a52;
        }
        QPushButton:pressed {
            background-color: #1e8449;
        }
    """

def get_generate_video_button_style():
    return """
        QPushButton {
            background-color: #e74c3c;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
        QPushButton:pressed {
            background-color: #a93226;
        }
    """

def get_visualize_button_style():
    return """
        QPushButton {
            background-color: #9b59b6;
        }
        QPushButton:hover {
            background-color: #8e44ad;
        }
        QPushButton:pressed {
            background-color: #7d3c98;
        }
    """ 