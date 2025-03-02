import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, 
    QSlider, QColorDialog, QHBoxLayout, QDialog, QFormLayout
)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer

USERNAME = "mail"
PASSWORD = "password"
HOST = "hostip"

def send_command(command):
    full_command = f'kasa --host {HOST} --username "{USERNAME}" --password "{PASSWORD}" {command}'
    try:
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Hata:", e)

def check_lamp_status():
    full_command = f'kasa --host {HOST} --username "{USERNAME}" --password "{PASSWORD}" feature state'
    try:
        result = subprocess.run(full_command, shell=True, check=True, capture_output=True, text=True)
        return "State (state): True" in result.stdout
    except subprocess.CalledProcessError as e:
        print("Hata:", e)
        return None

class SmartLampControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TapoControl")
        self.setFixedSize(350, 500)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.initUI()
        self.update_lamp_status()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_lamp_status)
        self.timer.start(10000)
    
    def initUI(self):
        layout = QVBoxLayout()
        
        title_layout = QHBoxLayout()
        self.logo_label = QLabel()

        image_path = os.path.join(os.path.dirname(__file__), "data", "image.png")
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"Hata: Resim yüklenemedi! Dosya yolu yanlış olabilir: {image_path}")
        else:
            self.logo_label.setPixmap(pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))

        self.title_label = QLabel("Tapo L530E Akıllı Ampul Kontrol")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        title_layout.addWidget(self.logo_label)
        title_layout.addWidget(self.title_label)
        layout.addLayout(title_layout)

        self.lamp_status_label = QLabel()
        self.lamp_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lamp_status_label)

        self.btn_on = QPushButton("\U0001F4A1 Lambayı Aç")
        self.btn_on.clicked.connect(self.turn_on)
        layout.addWidget(self.btn_on)

        self.btn_off = QPushButton("❌ Lambayı Kapat")
        self.btn_off.clicked.connect(self.turn_off)
        layout.addWidget(self.btn_off)

        self.brightness_label = QLabel("Parlaklık: 50%")
        layout.addWidget(self.brightness_label)

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.valueChanged.connect(self.update_brightness_label)
        layout.addWidget(self.brightness_slider)

        self.apply_brightness_btn = QPushButton("Uygula")
        self.apply_brightness_btn.clicked.connect(self.apply_brightness)
        layout.addWidget(self.apply_brightness_btn)

        layout.addWidget(QLabel("\nBeyaz Işık Modları"))
        self.btn_warm = QPushButton("🔥 Sıcak Beyaz (2500K)")
        self.btn_warm.clicked.connect(lambda: self.set_color_temp(2500))
        layout.addWidget(self.btn_warm)

        self.btn_cool = QPushButton("❄️ Soğuk Beyaz (6500K)")
        self.btn_cool.clicked.connect(lambda: self.set_color_temp(6500))
        layout.addWidget(self.btn_cool)

        layout.addWidget(QLabel("\nRenk Seçimi"))
        self.btn_color = QPushButton("🎨 Renk Seçimi")
        self.btn_color.clicked.connect(self.select_color)
        layout.addWidget(self.btn_color)

        self.setLayout(layout)
    
    def update_lamp_status(self):
        status = check_lamp_status()
        lamp_on_path = os.path.join(os.path.dirname(__file__), "data", "lamp_on.png")
        lamp_off_path = os.path.join(os.path.dirname(__file__), "data", "lamp_off.png")
        
        if status is None:
            self.lamp_status_label.setText("⚠️ Lamba Durumu Bilinmiyor")
            self.lamp_status_label.setPixmap(QPixmap())
        elif status:
            self.lamp_status_label.setPixmap(QPixmap(lamp_on_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.lamp_status_label.setPixmap(QPixmap(lamp_off_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))

    def turn_on(self):
        send_command("on")
        self.update_lamp_status()

    def turn_off(self):
        send_command("off")
        self.update_lamp_status()

    def apply_brightness(self):
        brightness = self.brightness_slider.value()
        send_command(f'brightness {brightness}')
        self.update_brightness_label()

    def update_brightness_label(self):
        self.brightness_label.setText(f"Parlaklık: {self.brightness_slider.value()}%")

    def set_color_temp(self, temp):
        send_command(f'feature color_temperature {temp}')

    def select_color(self):
        dialog = QColorDialog(self)
        kelvin_slider = QSlider(Qt.Orientation.Horizontal)
        kelvin_slider.setMinimum(2500)
        kelvin_slider.setMaximum(6500)
        kelvin_slider.setValue(4000)
        kelvin_slider.setTickInterval(100)
        kelvin_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        form = QFormLayout()
        form.addRow("Kelvin Değeri", kelvin_slider)
        dialog.layout().addLayout(form)

        if dialog.exec():
            color = dialog.selectedColor()
            kelvin_value = kelvin_slider.value()
            self.set_color_temp(kelvin_value)
            if color.isValid():
                h, s, v, _ = color.getHsv()
                send_command(f'hsv {h} {s} {v}')

if __name__ == "__main__":
    app = QApplication([])
    window = SmartLampControl()
    window.show()
    app.exec()
