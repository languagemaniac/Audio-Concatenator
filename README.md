# Audio-Concatenator
It concatenates your audio files. In order / randomly and with optional delay in between each of them


![audio concatenation - definitivo](https://github.com/languagemaniac/Audio-Concatenator/assets/43100450/e11bbf86-c260-42bf-87d9-93186e8634e6) 


The program currently provides support for a range of audio file formats, including mp3, wav, flac, and ogg. It allows you to choose between sequential or random concatenation of the selected files, and you can also specify a desired delay between each audio segment.

Adding a delay can be beneficial in language learning scenarios. For instance, you can record various phrases and set them to concatenate randomly. By incorporating a few seconds of delay between each phrase, you create an opportunity to repeat the phrase after hearing it before moving on to the next one. This technique allows for improved pronunciation practice and reinforces language retention.

## Running the Audio Concatenation App

The Audio Concatenation app allows you to concatenate audio files in various formats. To run the app, you need to install a few dependencies and ensure that `ffmpeg` is properly set up on your system.

### Prerequisites

Before running the app, make sure you have the following prerequisites installed:

- Python 3: The app is developed using Python, so you need to have Python 3 installed on your system. You can download Python from the official website: [python.org](https://www.python.org/).

### Installation

Follow these steps to install the required dependencies:

1. Clone the repository or download the source code to your local machine.

2. Open a terminal or command prompt and navigate to the project directory.

3. Create a new Python virtual environment (optional but recommended):

   ```bash
   python3 -m venv env
   ```

4. Activate the virtual environment:

   - For Windows:
     ```bash
     env\Scripts\activate
     ```

   - For macOS and Linux:
     ```bash
     source env/bin/activate
     ```

5. Install the dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

6. Install `ffmpeg`:

   - Windows:
     - Download `ffmpeg` from the official website: [ffmpeg.org](https://ffmpeg.org/download.html).
     - Extract the downloaded archive and add the `bin` directory to your system's PATH environment variable.

   - macOS (using Homebrew):
     ```bash
     brew install ffmpeg
     ```

   - Linux (using package manager):
     ```bash
     sudo apt-get install ffmpeg
     ```

### Running the App

Once you have installed the dependencies, you can run the Audio Concatenation app by following these steps:

1. Ensure that you are in the project directory and the virtual environment is activated (if you created one).

2. Run the app using Python:

   ```bash
   python Audio-Concatenator.py
   ```

3. The app window will open, allowing you to select audio files, set output options, and start the concatenation process.

4. Choose the audio files you want to concatenate by clicking the "Select Files" button.

5. Specify the output directory, output filename, output format, mixing order, and delay (if needed).

6. Click the "Start" button to begin the concatenation process.

7. Monitor the progress in the progress bar, and once completed, a message box will display the success message.

That's it! You have successfully run the Audio Concatenation app and concatenated audio files using different formats. Feel free to explore the app's features and customize it according to your requirements.
