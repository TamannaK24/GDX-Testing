import time
from gdx import gdx
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
)
from PySide6.QtCore import QTimer
import pyqtgraph as pg
import sys

SENSOR_OPTIONS = {
    "Force (N)": 1,
    "X-axis acceleration (m/s²)": 2,
    "Y-axis acceleration (m/s²)": 3,
    "Z-axis acceleration (m/s²)": 4,
    "X-axis gyro (rad/s)": 5,
    "Y-axis gyro (rad/s)": 6,
    "Z-axis gyro (rad/s)": 7,
}

class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GDX Sensor Graph")
        self.setGeometry(100, 100, 800, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Sensor selection
        self.sensor_label = QLabel("Select Sensor:")
        self.layout.addWidget(self.sensor_label)
        
        self.sensor_dropdown = QComboBox()
        self.sensor_dropdown.addItems(SENSOR_OPTIONS.keys())
        self.layout.addWidget(self.sensor_dropdown)

        # Sampling interval input
        self.interval_label = QLabel("Enter Sampling Interval (ms):")
        self.layout.addWidget(self.interval_label)

        self.interval_input = QLineEdit()
        self.interval_input.setPlaceholderText("e.g., 200")
        self.layout.addWidget(self.interval_input)

        self.status_label = QLabel("Press Start to Begin Data Collection")
        self.layout.addWidget(self.status_label)
        
        # Graph
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.getAxis("left").setTextPen("black")
        self.graph_widget.getAxis("bottom").setTextPen("black")
        self.graph_widget.setLabel("left", "Sensor Value")
        self.graph_widget.setLabel("bottom", "Time (s)")
        self.layout.addWidget(self.graph_widget)
        
        # Start and Stop buttons
        self.start_button = QPushButton("Start Data Collection")
        self.start_button.clicked.connect(self.start_collection)
        self.layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Data Collection")
        self.stop_button.clicked.connect(self.stop_collection)
        self.layout.addWidget(self.stop_button)
        
        # Table with 3 columns
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Time (s)", "Time (ms)", "Force (N)"])
        self.layout.addWidget(self.table)
        
        self.time_data = []
        self.sensor_data = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.collect_data)

        self.gdx_device = gdx.gdx()

    def start_collection(self):
        try:
            interval = int(self.interval_input.text())
        except ValueError:
            interval = 1000
            self.interval_input.setText("1000")

        sensor_name = self.sensor_dropdown.currentText()
        sensor_number = SENSOR_OPTIONS[sensor_name]

        self.graph_widget.clear()
        self.table.setRowCount(0)
        self.time_data.clear()
        self.sensor_data.clear()

        self.gdx_device.open(connection='usb', device_to_open="GDX-HD 15600161")
        self.gdx_device.select_sensors([sensor_number])
        self.gdx_device.start(interval)

        self.interval_ms = interval
        self.start_time = time.time()
        self.status_label.setText("Collecting Data...")
        self.timer.start(interval)

    def stop_collection(self):
        self.timer.stop()
        self.gdx_device.stop()
        self.gdx_device.close()
        self.status_label.setText("Data Collection Stopped")
        self.update_table()

    def collect_data(self):
        measurements = self.gdx_device.read()
        if measurements is None:
            self.stop_collection()
            return
        
        elapsed = time.time() - self.start_time
        timestamp_sec = round(elapsed, 3)
        timestamp_ms = int(elapsed * 1000)
        value = measurements[0]
        
        print(f"Timestamp: {timestamp_sec:.3f}s / {timestamp_ms}ms: {value}")
        self.time_data.append((timestamp_sec, timestamp_ms))
        self.sensor_data.append(value)
        self.update_plot()

    def update_plot(self):
        x_vals = [t[0] for t in self.time_data]
        self.graph_widget.plot(x_vals, self.sensor_data, pen='b', symbol='o', clear=True)

    def update_table(self):
        self.table.setRowCount(len(self.time_data))
        for i, ((sec, ms), val) in enumerate(zip(self.time_data, self.sensor_data)):
            self.table.setItem(i, 0, QTableWidgetItem(f"{sec:.3f}"))         # seconds as decimal
            self.table.setItem(i, 1, QTableWidgetItem(f"{ms:.1f}"))          # milliseconds as decimal
            self.table.setItem(i, 2, QTableWidgetItem(f"{val:.3f}"))         # force value as decimal

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    sys.exit(app.exec())
