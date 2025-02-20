from gdx import gdx
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton
from PySide6.QtCore import QTimer
import pyqtgraph as pg

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gdx = gdx.gdx()
        self.initUI()

        # Data storage for graph
        self.time_data = []
        self.force_data = []
        self.counter = 0  # Keeps track of time steps
        self.duration = 10  # Default recording time (seconds)

    def initUI(self):
        self.setWindowTitle("GDX Graphing - Force vs Time")
        self.setGeometry(100, 100, 800, 500)

        # Create PyQtGraph plot widget
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setLabel('left', 'Force (N)')
        self.graphWidget.setLabel('bottom', 'Time (s)')
        self.graphWidget.setTitle("Force vs Time")
        self.graphWidget.showGrid(x=True, y=True)

        # Set pen color (blue)
        self.pen = pg.mkPen(color=(0, 0, 255), width=2)

        # Label to display text data
        self.label = QLabel("Enter duration (seconds) and press Start", self)

        # Input field for user to enter recording duration
        self.duration_input = QLineEdit(self)
        self.duration_input.setPlaceholderText("Enter duration in seconds")

        # Start button to begin recording
        self.start_button = QPushButton("Start Recording", self)
        self.start_button.clicked.connect(self.start_collection)

        # Layout setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.duration_input)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.graphWidget)  # Add graph to layout

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Initialize the graph plot
        self.plot_data = self.graphWidget.plot([], [], pen=self.pen)

    def start_collection(self):
        """Starts data collection when user clicks the button."""
        try:
            # Get user input for duration
            user_input = self.duration_input.text()
            if user_input.isdigit():
                self.duration = int(user_input)
            else:
                self.label.setText("Invalid input! Enter a valid number.")
                return

            # Reset data
            self.time_data = []
            self.force_data = []
            self.counter = 0

            self.gdx.open(connection='usb', device_to_open="GDX-HD 15600161")

            # Select force sensor (assuming it's at index 1)
            self.gdx.select_sensors([1])  
            self.gdx.start()

            column_headers = self.gdx.enabled_sensor_info()
            print('\nSelected Sensors:', column_headers)

            self.label.setText(f"Recording for {self.duration} seconds...")

            # Timer to update data every second
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_data)
            self.timer.start(1000)  # Every 1000ms (1 second)

            # Stop recording after duration ends
            self.stop_timer = QTimer()
            self.stop_timer.singleShot(self.duration * 1000, self.stop_collection)

        except Exception as e:
            print(f"Error initializing sensor: {e}")
            self.label.setText("Error: Could not initialize sensor")

    def update_data(self):
        """Reads new data and updates graph."""
        try:
            measurements = self.gdx.read()
            if measurements is None:
                print("No data received. Stopping collection.")
                self.stop_collection()
                return

            force_value = measurements[0]  # Assuming force sensor is first

            # Store data for graph
            self.time_data.append(self.counter)
            self.force_data.append(force_value)
            self.counter += 1

            # Update QLabel text
            self.label.setText(f"Latest Measurement: {force_value} N")

            # Update graph with new data
            self.plot_data.setData(self.time_data, self.force_data)

        except Exception as e:
            print(f"Error reading sensor data: {e}")
            self.label.setText("Error: Could not read sensor data")
            self.stop_collection()

    def stop_collection(self):
        """Stops data collection and prints all recorded points."""
        print("\nRecording complete. Data points collected:")
        print(list(zip(self.time_data, self.force_data)))

        self.label.setText("Recording Complete! Check console for data.")
        self.timer.stop()
        self.gdx.stop()
        self.gdx.close()

    def closeEvent(self, event):
        """Handles closing event to safely stop sensors."""
        print("Closing application and stopping sensor...")
        self.gdx.stop()
        self.gdx.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec())
