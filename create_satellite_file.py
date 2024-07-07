import os
import sys
import poplib
import email
from datetime import date, datetime, time
import time as tm
from email.header import decode_header
import glob
import secrets as sec


def extract_hour(filename):
    return int(filename[-8:-4])


def decode_subject(subject):
    decoded_subject = decode_header(subject)
    return (
        decoded_subject[0][0].decode(decoded_subject[0][1])
        if decoded_subject[0][1]
        else decoded_subject[0][0]
    )


def append_file_contents(source_file, destination_file):
    with open(source_file, "r") as source:
        with open(destination_file, "w+") as destination:
            for _ in range(6):
                next(source)
            for line in source:
                destination.write(line)


def copy_file_contents(source_file, destination_file, destination_file2):
    matching_files = glob.glob(source_file)
    if matching_files:
        file_hours = [extract_hour(filename) for filename in matching_files]
        max_hour_index = file_hours.index(max(file_hours))
        most_recent_file = matching_files[max_hour_index]

        print("ΕΛΛΗΝΙΚΟ ΑΡΧΕΙΟ:", most_recent_file)
        append_file_contents(most_recent_file, destination_file)
        append_file_contents(most_recent_file, destination_file2)
    else:
        print("ΤΟ ΕΛΛΗΝΙΚΟ ΑΡΧΕΙΟ ΔΕΝ ΒΡΕΘΗΚΕ ΣΤΟΝ ΦΑΚΕΛΟ EMK_DATA!")
        print("ΤΟ ΤΕΛΙΚΟ ΑΡΧΕΙΟ ΔΕΝ ΔΗΜΙΟΥΡΓΗΘΗΚΕ!")
        input('ΠΑΤΗΣΤΕ ΤΟ "ENTER" ΓΙΑ ΝΑ ΚΛΕΙΣΕΤΕ ΤΟ ΠΑΡΑΘΥΡΟ...')
        # tm.sleep(3)
        sys.exit()


def append_email_contents(email_contents, destination_file, insert_type):
    with open(destination_file, insert_type) as file:
        lines = email_contents.split("\n")[1:]
        for line in lines:
            file.write(line + "\n")


def remove_empty_lines_and_replace_ext(file_path):
    with open(file_path, "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line.strip() and chr(3) in line:
                line = "\n"
                file.write(line)
            elif line.startswith("\0"):
                continue
            elif line.strip():
                file.write(line)
        file.truncate()


def get_mail(target_subject, insert_type):
    pop3_server = secrets.pop3_server
    username = secrets.username
    password = secrets.password
    mail_server = poplib.POP3_SSL(pop3_server)
    mail_server.user(username)
    mail_server.pass_(password)
    destination_file = sec.destination_file
    destination_file2 = sec.destination_file2
    resp, mails, _ = mail_server.list()
    email_index = None
    for i in range(len(mails), 0, -1):
        _, email_data, _ = mail_server.retr(i)
        email_content = b"\n".join(email_data).decode("utf-8", errors="ignore")
        if email_content is not None:
            msg = email.message_from_string(email_content)
            subject = decode_subject(msg.get("Subject", ""))
            if subject.startswith(target_subject):
                print("ΓΑΛΛΙΚΟ EMAIL:", subject[:18])
                email_index = i
                break

    if email_index is not None:
        _, email_data, _ = mail_server.retr(email_index)
        email_content = b"\n".join(email_data).decode("utf-8", errors="ignore")
        msg = email.message_from_string(email_content)

        email_contents = msg.get_payload()
        append_email_contents(email_contents, destination_file, insert_type)
        append_email_contents(email_contents, destination_file2, insert_type)

        mail_server.quit()
    else:
        print("ΔΕΝ ΒΡΕΘΗΚΕ ΓΑΛΛΙΚΟ EMAIL GALE ΜΕ ΣΗΜΕΡΙΝΗ ΗΜΝΙΑ ΣΤΟΝ EMAIL SERVER!")
        print("ΤΟ ΤΕΛΙΚΟ ΑΡΧΕΙΟ ΔΕΝ ΔΗΜΙΟΥΡΓΗΘΗΚΕ!")
        input('ΠΑΤΗΣΤΕ ΤΟ "ENTER" ΓΙΑ ΝΑ ΚΛΕΙΣΕΤΕ ΤΟ ΠΑΡΑΘΥΡΟ...')
        # tm.sleep(3)
        sys.exit()


def main():
    day = date.today().strftime("%d")
    final = ""

    if len(sys.argv) == 1:
        choice1 = int(input("ΕΠΙΛΕΞΤΕ: (ΘΑΛΑΣΣΕΣ -> 1, GALE -> 2): "))
        if choice1 == 1:
            final = "sea"
        elif choice1 == 2:
            choice2 = int(input("GALE: (ΕΛΛΗΝΙΚΟ -> 1, ΓΑΛΛΙΚΟ -> 2): "))
            if choice2 == 1:
                final = "greek"
            elif choice2 == 2:
                final = "french"
            else:
                sys.exit()
        else:
            sys.exit()
    elif len(sys.argv) == 2:
        if sys.argv[1] == "1":
            final = "sea"
        elif sys.argv[1] == "2":
            final = "greek"
        elif sys.argv[1] == "3":
            final = "french"

    os.chdir(sec.emk_folder)
    destination_file = sec.destination_file
    destination_file2 = sec.destination_file2

    if final == "sea":
        current_time = datetime.now().time()
        time_to_compare = time(16, 0)  # 16:00

        if current_time < time_to_compare:
            source_file = "G_FQME24LGAT" + day + "0800.---"
        elif current_time > time_to_compare:
            source_file = "G_FQME28LGAT" + day + "2000.---"
        else:
            sys.exit()

        copy_file_contents(source_file, destination_file, destination_file2)
        get_mail("FQMQ54 LFPW " + day, "a")
    elif final == "greek":
        source_file = "G_WWME22LGAT" + day + "????*.---"
        copy_file_contents(source_file, destination_file, destination_file2)
    elif final == "french":
        get_mail("WOMQ50 LFPW " + day, "w")

    remove_empty_lines_and_replace_ext(destination_file)
    print("SATELLITE FILE CREATED SUCCESFULLY! (LOCALLY)")
    remove_empty_lines_and_replace_ext(destination_file2)
    print("SATELLITE FILE CREATED SUCCESFULLY! (VIRTUAL MACHINE)")
    tm.sleep(3)


if __name__ == "__main__":
    main()
