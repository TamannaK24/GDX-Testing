import time
from gdx import gdx
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QTimer
import pyqtgraph as pg
import sys

class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time vs Force Graph")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.label = QLabel("Press Start to Begin Data Collection")
        self.label.setStyleSheet("color: black;")
        self.layout.addWidget(self.label)
        
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.getAxis("left").setTextPen("black")
        self.graph_widget.getAxis("bottom").setTextPen("black")
        self.graph_widget.setLabel("left", "Force (N)")
        self.graph_widget.setLabel("bottom", "Time (seconds)")
        self.layout.addWidget(self.graph_widget)
        
        self.start_button = QPushButton("Start Data Collection")
        self.start_button.clicked.connect(self.start_collection)
        self.layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Data Collection")
        self.stop_button.clicked.connect(self.stop_collection)
        self.layout.addWidget(self.stop_button)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Time (s)", "Force (N)"])
        self.layout.addWidget(self.table)
        
        self.time_data = []
        self.force_data = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.collect_data)
        
        self.gdx_device = gdx.gdx()
        self.gdx_device.open(connection='usb', device_to_open="GDX-HD 15600161")
        self.gdx_device.select_sensors([1])  # Selecting Force (N) sensor
        self.gdx_device.start(1000)  # Set sampling interval (ms)
        
        self.current_time = 0

    def start_collection(self):
        self.time_data.clear()
        self.force_data.clear()
        self.graph_widget.clear()
        self.table.setRowCount(0)
        self.current_time = 0
        self.label.setText("Collecting Data...")
        self.timer.start(1000)

    def stop_collection(self):
        self.timer.stop()
        self.gdx_device.stop()
        self.gdx_device.close()
        self.label.setText("Data Collection Stopped")
        self.update_table()

    def collect_data(self):
        measurements = self.gdx_device.read()
        if measurements is None:
            self.stop_collection()
            return
        
        self.current_time += 1
        self.time_data.append(self.current_time)
        self.force_data.append(measurements[0])
        
        print(f"Time {self.current_time}s: {measurements[0]}")
        self.update_plot()

    def update_plot(self):
        self.graph_widget.plot(self.time_data, self.force_data, pen='b', symbol='o', clear=True)

    def update_table(self):
        self.table.setRowCount(len(self.time_data))
        for i, (time_val, force_val) in enumerate(zip(self.time_data, self.force_data)):
            self.table.setItem(i, 0, QTableWidgetItem(str(time_val)))
            self.table.setItem(i, 1, QTableWidgetItem(str(force_val)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    sys.exit(app.exec())
