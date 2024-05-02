# Gale Monitoring Program

The Gale Monitoring Program is a Python application designed to monitor incoming emails for specific subjects and process files in a designated folder. It performs the following tasks:

- **Email Monitoring**: Monitors incoming emails via POP3 server for specific subjects.
- **File Processing**: Processes newly created files in a specified folder.
- **Audio Notification**: Plays audio notifications for certain events.
- **System Tray Integration**: Provides a system tray icon for easy access to program controls.

## Features

- **Email Monitoring**: The program checks for new emails matching specific criteria and processes them accordingly.
- **File Processing**: Monitors a designated folder for newly created files and performs actions based on file names.
- **Audio Notifications**: Plays audio notifications for important events, such as successful processing of files.
- **System Tray Integration**: Offers a system tray icon for easy access to program functions, including showing/hiding the console window and exiting the program.

## Usage

1. Ensure that Python and required dependencies are installed.
2. Set up email credentials and other configuration parameters in the `secrets.py` file.
3. Run the program using the provided Python script.
4. Keep the program running to continuously monitor emails and folders.

## Configuration

Modify the `secrets.py` file to customize settings such as email credentials, folder paths, and other parameters.

## Dependencies

- Python 3.x
- Pygame
- Pystray
- Watchdog
- Tkinter (included in Python standard library)

## Installation

1. Clone the repository to your local machine.
2. Install Python and required dependencies.
3. Set up configuration parameters in the `secrets.py` file.
4. Run the program using the provided Python script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Special thanks to the developers of Pygame, Pystray, and Watchdog for their excellent libraries.

