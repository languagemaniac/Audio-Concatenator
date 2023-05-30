from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QRadioButton, QProgressBar, QMessageBox, QFileDialog, QComboBox
from PyQt5.QtCore import Qt
from pydub import AudioSegment
from pydub.playback import play
import random
import os
import shutil


def mix_audio_files(files, output_file, progress_bar, source_directory, save_to_source=False, mixing_order="sequential", delay=0):
    files = list(files)

    if mixing_order == "random":
        combined_audio = AudioSegment.empty()

        total_files = len(files)

        for i in range(total_files):
            random_file = random.choice(files)
            audio = AudioSegment.from_file(random_file)

            if combined_audio:
                if delay > 0:
                    silent_segment = AudioSegment.silent(duration=int(delay * 1000))
                    combined_audio += silent_segment

            combined_audio += audio
            files.remove(random_file)

            remaining_files = len(files)
            progress = int(((total_files - remaining_files) / total_files) * 100)
            progress_bar.setValue(progress)

    else:  # Sequential order
        combined_audio = AudioSegment.from_file(files[0])

        total_files = len(files) - 1  # Exclude the first file

        for i in range(1, len(files)):
            audio = AudioSegment.from_file(files[i])

            if delay > 0:
                silent_segment = AudioSegment.silent(duration=int(delay * 1000))
                combined_audio += silent_segment

            combined_audio += audio

            remaining_files = total_files - i
            progress = int(((total_files - remaining_files) / total_files) * 100)
            progress_bar.setValue(progress)

    output_format = os.path.splitext(output_file)[1][1:].lower()

    combined_audio.export(output_file, format=output_format)

    if save_to_source:
        output_filename = os.path.basename(output_file)
        output_path = os.path.join(source_directory, output_filename)
        if output_file != output_path:
            shutil.move(output_file, output_path)

    progress_bar.setValue(100)
    QMessageBox.information(None, 'Audio Concatenation', 'Audio files successfully mixed and saved.')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Audio Concatenation')
        self.resize(600, 200)

        # Connect the toggle_output_directory_elements method to the stateChanged signal
        self.use_source_checkbox = QCheckBox('Use Source')
        self.use_source_checkbox.stateChanged.connect(self.toggle_output_directory_elements)

        # Create central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create file selection area
        file_layout = QHBoxLayout()
        self.file_label = QLabel('Audio Files:')
        self.file_list = QLineEdit()
        self.file_select_button = QPushButton('Select Files')
        self.file_select_button.clicked.connect(self.select_files)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_list)
        file_layout.addWidget(self.file_select_button)
        main_layout.addLayout(file_layout)

        # Create output directory selection area
        output_layout = QHBoxLayout()
        self.output_directory_label = QLabel('Output Directory:')
        self.output_directory_entry = QLineEdit()
        self.output_directory_select_button = QPushButton('Select Output Directory')
        self.output_directory_select_button.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_directory_label)
        output_layout.addWidget(self.output_directory_entry)
        output_layout.addWidget(self.output_directory_select_button)
        output_layout.addWidget(self.use_source_checkbox)
        main_layout.addLayout(output_layout)

        # Create output filename entry
        self.output_filename_label = QLabel('Output Filename:')
        self.output_filename_entry = QLineEdit()
        main_layout.addWidget(self.output_filename_label)
        main_layout.addWidget(self.output_filename_entry)

        # Create output format selection
        self.format_label = QLabel('Output Format:')
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(['mp3', 'wav', 'flac', 'ogg'])
        main_layout.addWidget(self.format_label)
        main_layout.addWidget(self.format_combobox)

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

        # Create start button
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_mixing)
        main_layout.addWidget(self.start_button)

        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        main_layout.addWidget(self.progress_bar)

    def toggle_output_directory_elements(self, state):
        # Disable/enable the output directory elements based on the state of the checkbox
        self.output_directory_entry.setEnabled(state != Qt.Checked)
        self.output_directory_select_button.setEnabled(state != Qt.Checked)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select Audio Files')
        self.file_list.setText('\n'.join(files))

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        self.output_directory_entry.setText(directory)

    def start_mixing(self):
        files = self.file_list.text().split('\n')
        output_directory = self.output_directory_entry.text()
        output_filename = self.output_filename_entry.text().strip()
        output_format = self.format_combobox.currentText()
        source_directory = None
        delay = 0.0  # Default delay value

        if self.use_source_checkbox.isChecked():
            source_directory, _ = os.path.split(files[0])

        # Check if output filename is empty
        if not output_filename:
            QMessageBox.critical(self, 'Error', 'Please enter an output filename.')
            return

        # Check if delay entry is empty or invalid
        delay_text = self.delay_entry.text().strip()
        if delay_text:
            try:
                delay = float(delay_text)
            except ValueError:
                QMessageBox.critical(self, 'Error', 'Invalid delay value. Please enter a valid number.')
                return

        output_file = os.path.join(output_directory, f"{output_filename}.{output_format}")

        mix_audio_files(
            files,
            output_file,
            self.progress_bar,
            source_directory,
            self.use_source_checkbox.isChecked(),
            "sequential" if self.sequential_radio.isChecked() else "random",
            delay
        )


if __name__ == '__main__':
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    app.exec_()
