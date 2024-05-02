import poplib
from email.parser import Parser
from datetime import datetime, timedelta, date
import time
import subprocess
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import pystray
from PIL import Image
import ctypes
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import messagebox
import logging
import secrets

print("ΠΑΡΑΚΑΛΩ ΠΕΡΙΜΕΝΕΤΕ ΝΑ ΕΜΦΑΝΙΣΤΟΥΝ ΤΑ EMAILS ΚΑΙ ΜΗΝ ΚΛΕΙΣΕΤΕ ΑΥΤΟ ΤΟ ΠΑΡΑΘΥΡΟ!")
print("ΜΟΛΙΣ ΕΜΦΑΝΙΣΤΟΥΝ ΜΠΟΡΕΙΤΕ ΑΠΟ ΤΟ ΕΙΚΟΝΙΔΙΟ ΚΑΤΩ ΔΕΞΙΑ ΝΑ ΕΠΙΛΕΞΕΤΕ 'ΑΠΟΚΡΥΨΗ' ΓΙΑ ΝΑ ΚΡΥΨΕΤΕ ΤΟ ΠΑΡΑΘΥΡΟ")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up constants from secrets module
pop3_server = secrets.pop3_server
username = secrets.username
password = secrets.password
python_path = secrets.python_path
create_sat_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'create_satellite_file.py')
greek_mp3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sounds', 'greek_gale.mp3')
french_mp3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sounds', 'french_gale.mp3')
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wind_icon.png')
folder_to_watch = secrets.emk_folder
file_prefix = 'G_WWME22LGAT'
specific_text = f'WOMQ50 LFPW {date.today().strftime("%d")}'

# Initialize processed_emails set
processed_emails = set()

def get_unread_emails(username, password, pop3_server, processed_emails):
    """Retrieve unread emails from POP3 server."""
    try:
        # Connect to the POP3 server
        pop_conn = poplib.POP3(pop3_server)
        pop_conn.user(username)
        pop_conn.pass_(password)

        # Get information about the mailbox
        num_messages, _ = pop_conn.stat()

        # Retrieve emails
        unread_emails = []
        for i in range(num_messages):
            _, email_lines, _ = pop_conn.retr(i + 1)
            email_content = b'\n'.join(email_lines).decode('utf-8', errors='ignore')
            email_parser = Parser()
            email = email_parser.parsestr(email_content)
            email_id = email['Message-ID']
            if email_id not in processed_emails:
                unread_emails.append(email)
                logger.info("Updated processed email: %s", email['Subject'])
                processed_emails.add(email_id)  # Add email ID to processed_emails

        return unread_emails
    except Exception as e:
        logger.error("Error retrieving emails: %s", e)
        return []


def handle_new_emails():
    """Handle new emails."""
    while True:
        unread_emails = get_unread_emails(username, password, pop3_server, processed_emails)
        for email in unread_emails:
            logger.info("From: %s", email['From'])
            logger.info("Subject: %s", email['Subject'])

            if email['Subject'] and email['Subject'].startswith(specific_text):
                email_timestamp = get_email_timestamp(email)
                current_time = datetime.now()
                time_difference = current_time - email_timestamp
                if time_difference < timedelta(minutes=30):
                    subprocess.run([python_path, create_sat_script, '3'])
                    play_mp3_thread = threading.Thread(target=play_mp3_file, args=(french_mp3,))
                    show_success_thread = threading.Thread(target=show_success_message, args=("French",))
                    play_mp3_thread.start()
                    show_success_thread.start()

        time.sleep(60)


def get_email_timestamp(email):
    """Parse email date string into datetime object."""
    email_date_str = email['Date'].replace('GMT', '').strip()
    date_formats = ['%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S']
    for fmt in date_formats:
        try:
            return datetime.strptime(email_date_str, fmt)
        except ValueError:
            pass
    return None


def play_mp3_file(mp3_file):
    """Play MP3 file."""
    try:
        pygame.init()
        pygame.mixer.music.load(mp3_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.quit()
    except Exception as e:
        logger.error("Error playing MP3 file: %s", e)


def show_success_message(country):
    """Show success message."""
    try:
        root = tk.Tk()
        root.withdraw()
        if country == "French":
            msg_text = "Έγινε λήψη και μετατροπή του Γαλλικού Gale!"
        elif country == "Greek":
            msg_text = "Έγινε λήψη και μετατροπή του Ελληνικού Gale!"
        messagebox.showinfo("Προσοχή!", msg_text)
        root.destroy()
    except Exception as e:
        logger.error("Error showing success message: %s", e)


class FileCreatedHandler(FileSystemEventHandler):
    """Handler for created files."""

    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory:
            return

        if event.src_path.startswith(folder_to_watch) and os.path.basename(event.src_path).startswith(file_prefix):
            logger.info("Ανιχνεύτηκε νέο αρχείο Ελληνικού Gale: %s", event.src_path)
            try:
                subprocess.run([python_path, create_sat_script, '2'])
                play_mp3_thread = threading.Thread(target=play_mp3_file, args=(greek_mp3,))
                show_success_thread = threading.Thread(target=show_success_message, args=("Greek",))
                play_mp3_thread.start()
                show_success_thread.start()
            except Exception as e:
                logger.error("Error processing file: %s", e)


def create_system_tray_icon():
    """Create system tray icon and menu."""
    try:
        icon_image = Image.open(icon_path)
        menu = (
            pystray.MenuItem('Εμφάνιση/Απόκρυψη', toggle_console_window),
            pystray.MenuItem('Έξοδος', exit_program)
        )
        icon = pystray.Icon('check_for_email', icon_image, 'Έλεγχος για Gale', menu)
        icon.run()
    except Exception as e:
        logger.error("Error creating system tray icon: %s", e)


def toggle_console_window(icon, item):
    """Toggle console window visibility."""
    global console_visible
    console_visible = not console_visible
    if console_visible:
        show_console_window()
    else:
        hide_console_window()


def hide_console_window():
    """Hide console window."""
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)


def show_console_window():
    """Show console window."""
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 1)


def exit_program(icon, item):
    """Exit the program."""
    icon.stop()
    os._exit(0)


if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW("Έλεγχος για Gale")

    email_thread = threading.Thread(target=handle_new_emails)
    email_thread.daemon = True
    email_thread.start()

    event_handler = FileCreatedHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()

    create_system_tray_icon()
