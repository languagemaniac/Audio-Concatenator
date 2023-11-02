from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QRadioButton, QProgressBar, QMessageBox, QFileDialog, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pydub import AudioSegment
import os
import random
import shutil
from concurrent.futures import ThreadPoolExecutor

class AudioConcatenator(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    canceled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.input_directory = ""
        self.output_directory = ""
        self.output_filename = ""
        self.use_source_directory = False
        self.mixing_order = "sequential"
        self.delay = 0
        self.cancelled = False

    def run(self):
        if not os.path.exists(self.input_directory) or not os.path.isdir(self.input_directory):
            self.canceled.emit()
            return

        files = [os.path.join(self.input_directory, filename) for filename in os.listdir(self.input_directory) if filename.lower().endswith(('.mp3', '.wav', '.flac', '.ogg'))]

        if not files:
            self.canceled.emit()
            return

        if self.mixing_order == "random":
            random.shuffle(files)

        total_files = len(files)
        combined_audio = AudioSegment.empty()

        with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust the number of workers as needed
            futures = []

            for i, file in enumerate(files):
                if self.cancelled:
                    return

                future = executor.submit(self.process_audio, file, i, total_files)
                futures.append(future)

            for future in futures:
                combined_audio += future.result()

        output_format = "mp3"  # Change to the desired output format
        output_file = os.path.join(self.output_directory, f"{self.output_filename}.{output_format}")

        combined_audio.export(output_file, format=output_format)

        if self.use_source_directory:
            self.output_directory = self.input_directory

        self.finished.emit()

    def process_audio(self, file, index, total_files):
        audio = AudioSegment.from_file(file)

        if index > 0 and self.delay > 0:
            silent_segment = AudioSegment.silent(duration=int(self.delay * 1000))
            combined_audio = silent_segment + audio
        else:
            combined_audio = audio

        self.progress.emit(int(((index + 1) / total_files) * 100))
        return combined_audio

    def cancel(self):
        self.cancelled = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Audio Concatenation')
        self.resize(600, 200)

        # Create central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create input directory selection area
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Audio Directory:')
        self.input_list = QLineEdit()
        self.input_select_button = QPushButton('Select Directory')
        self.input_select_button.clicked.connect(self.select_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_list)
        input_layout.addWidget(self.input_select_button)
        main_layout.addLayout(input_layout)

        # Create output directory selection area
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory:')
        self.output_list = QLineEdit()
        self.output_select_button = QPushButton('Select Output Directory')
        self.output_select_button.clicked.connect(self.select_output_directory)
        self.use_source_checkbox = QCheckBox('Use Source Directory')
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_list)
        output_layout.addWidget(self.output_select_button)
        output_layout.addWidget(self.use_source_checkbox)
        main_layout.addLayout(output_layout)

        # Create output filename entry
        self.output_filename_label = QLabel('Output Filename:')
        self.output_filename_entry = QLineEdit()
        main_layout.addWidget(self.output_filename_label)
        main_layout.addWidget(self.output_filename_entry)

        # Create mixing order selection
        self.mixing_order_label = QLabel('Mixing Order:')
        self.sequential_radio = QRadioButton('Sequential')
        self.random_radio = QRadioButton('Random')
        self.random_radio.setChecked(True)
        mixing_order_layout = QHBoxLayout()
        mixing_order_layout.addWidget(self.mixing_order_label)
        mixing_order_layout.addWidget(self.sequential_radio)
        mixing_order_layout.addWidget(self.random_radio)
        main_layout.addLayout(mixing_order_layout)

        # Create delay entry
        self.delay_label = QLabel('Delay between audio files (seconds):')
        self.delay_entry = QLineEdit()
        main_layout.addWidget(self.delay_label)
        main_layout.addWidget(self.delay_entry)

        # Create output format selection
        self.format_label = QLabel('Output Format:')
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(['mp3', 'wav', 'flac', 'ogg'])
        main_layout.addWidget(self.format_label)
        main_layout.addWidget(self.format_combobox)

        # Create buttons layout
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton('Start')
        self.cancel_button = QPushButton('Cancel')
        self.start_button.clicked.connect(self.start_mixing)
        self.cancel_button.clicked.connect(self.cancel_mixing)
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)

        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        main_layout.addWidget(self.progress_bar)

        # Create and connect audio concatenator signals
        self.audio_concatenator = AudioConcatenator()
        self.audio_concatenator.progress.connect(self.update_progress)
        self.audio_concatenator.finished.connect(self.process_finished)
        self.audio_concatenator.canceled.connect(self.process_canceled)

    def select_input_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Audio Directory')
        self.input_list.setText(directory)

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        self.output_list.setText(directory)

    def start_mixing(self):
        input_directory = self.input_list.text()
        output_directory = self.output_list.text()
        output_filename = self.output_filename_entry.text().strip()
        delay = 0.0  # Default delay value
        output_format = self.format_combobox.currentText()  # Get selected format

        if not output_filename:
            QMessageBox.critical(self, 'Error', 'Please enter an output filename.')
            return

        delay_text = self.delay_entry.text().strip()
        if delay_text:
            try:
                delay = float(delay_text)
            except ValueError:
                QMessageBox.critical(self, 'Error', 'Invalid delay value. Please enter a valid number.')
                return

        use_source_directory = self.use_source_checkbox.isChecked()
        mixing_order = "sequential" if self.sequential_radio.isChecked() else "random"

        # Configure and start the audio concatenation process
        self.audio_concatenator.input_directory = input_directory
        self.audio_concatenator.output_directory = output_directory
        self.audio_concatenator.output_filename = output_filename
        self.audio_concatenator.use_source_directory = use_source_directory
        self.audio_concatenator.mixing_order = mixing_order
        self.audio_concatenator.delay = delay

        self.start_button.setDisabled(True)
        self.cancel_button.setDisabled(False)
        self.audio_concatenator.start()

    def cancel_mixing(self):
        self.audio_concatenator.cancel()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def process_finished(self):
        self.start_button.setDisabled(False)
        self.cancel_button.setDisabled(True)
        QMessageBox.information(None, 'Audio Concatenation', 'Audio files successfully mixed and saved.')

    def process_canceled(self):
        self.start_button.setDisabled(False)
        self.cancel_button.setDisabled(True)
        self.progress_bar.reset()

if __name__ == '__main__':
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    app.exec()
