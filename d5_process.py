import poplib
import email
from email.header import decode_header
import pandas as pd
from datetime import datetime, date, timedelta
import numpy as np
import os
import sys
import variables
from tkinter import messagebox
from metar_db import query_insert, query_insert_2
sys.path.append(variables.script_path)

print("ΚΑΛΗΣΠΕΡΑ Δ5. Η ΔΙΑΔΙΚΑΣΙΑ ΞΕΚΙΝΗΣΕ. ΠΑΡΑΚΑΛΩ ΜΗΝ ΠΕΙΡΑΞΕΤΕ ΤΟ ΠΛΑΙΣΙΟ ΑΥΤΟ!")

###target path
target_pth = variables.target_path
# Connect to email server
poplib._MAXLINE = 20480
pop_conn = poplib.POP3(variables.pop3_server)
pop_conn.user(variables.username)
pop_conn.pass_(variables.password)
ZZmails = []
num_of_mails = len(pop_conn.list()[1])
print(num_of_mails)

yesterday = date.today() - timedelta(1)
desired_subject = "ZZD5" + yesterday.strftime("%d%m%Y")
print("PSAXNOYME=" + desired_subject)

for i in range(num_of_mails):
    raw_email = b"\n".join(pop_conn.retr(i + 1)[1])
    parsed_email = email.message_from_bytes(raw_email)
    if not (parsed_email["Subject"]):
        parse_subject = "KENO"
    else:
        parse_subject = parsed_email["Subject"]
    header1 = decode_header(parse_subject).pop()
    subject = str(header1)
    enco = header1[-1]
    if desired_subject in subject:
        print("BRHKA=" + subject)
        print("AYTO TO THELOYME " + enco)
        wanted_email = str(parsed_email.get_payload(decode=True)).replace("\\n", "\n")
        ZZmails.append(wanted_email)
        target_subj = subject.split("ZZD5")[1].split(",")[0].replace("'", "")
pop_conn.quit()

target_title = "Metar_Reporting_" + target_subj + ".xlsx"
print("TITLOS=" + target_title)
if target_title in os.listdir(target_pth):
    messagebox.showinfo("D5", "Το αρχείο excel έχει ήδη δημιουργηθεί!")
    msg_forthebox = (
        "Το αρχείο excel έχει ήδη δημιουργηθεί! Επαναλάβατε την διαδικασία σωστά."
    )
else:
    example = ZZmails[-1]
    ZZmails = []
    example_ls = example.split("\n")
    aux = list(filter(None, example_ls[:-2]))
    header = [
        "Insertion_datetime",
        "Bulletin",
        "Station",
        "Predicted_datetime",
        "Delay_in_sec",
        "Sender",
        "Correction",
        "Delayed",
        "IDD",
    ]
    df = pd.DataFrame(columns=header)

    i = 0
    while i <= len(aux) - 1:
        ln = aux[i]
        if ln[0:2] == "b'":
            ln = ln[2:]
        print(ln)

        c_1 = str(ln.split(",")[0] + ln.split(",")[1])
        c_1 = c_1.replace("2E", ".")
        c_1 = datetime.strptime(c_1, "%d.%m.%Y %H:%M:%S")

        # Bulletin, Station, Appropriate time block
        aux2 = ln.split(",")[2]
        aux3 = aux2.split(" ")
        c_2 = aux3[1]  # bulletin
        c_3 = aux3[2]  # Station
        bulletinday = aux3[3][:2]
        # last date of the previous month
        ldpm = c_1.replace(day=1) - timedelta(days=1)

        if c_1.day < int(bulletinday):
            bulletinmonth = ldpm.month
        else:
            bulletinmonth = c_1.month

        c_4 = (
            bulletinday
            + "."
            + str(bulletinmonth)
            + "."
            + str(c_1.year)
            + " "
            + aux3[3][2:4]
            + ":"
            + aux3[3][4:6]
        )

        c_4 = datetime.strptime(c_4, "%d.%m.%Y %H:%M")  # Predicted datetime
        # delay in sec block
        c_5 = int((c_1 - c_4).total_seconds())
        # Sender block
        c_6 = ln.split(",")[7]
        # correction block
        c_7 = "No Correction" if len(aux2.split(" ")) < 5 else aux2.split(" ")[4]
        # delayed block

        if c_7 == "No Correction" and c_4.minute in [0, 10, 30, 40] and c_5 > 600:
            c_8 = 1
        elif c_7 == "No Correction" and c_4.minute in [20, 50] and c_5 > 300:
            c_8 = 1
        else:
            c_8 = 0
        # injustified days difference
        fake_var = int((c_1 - c_4).days)
        c_9 = fake_var if (fake_var > 0 and c_7 != "No Correction") else 0
        # data frame insertion
        row = pd.DataFrame(
            {
                "Insertion_datetime": c_1,
                "Bulletin": c_2,
                "Station": c_3,
                "Predicted_datetime": c_4,
                "Delay_in_sec": c_5,
                "Sender": c_6,
                "Correction": c_7,
                "Delayed": c_8,
                "IDD": c_9,
            },
            index=[0],
        )
        df = pd.concat([df, row], ignore_index=True)
        i += 1

    d_5 = df.loc[df.Delayed == 1]
    d_5 = d_5.loc[
        (d_5.Station.astype(str).str[0] == "L")
        & (d_5.Station.astype(str).str[1] == "G")
    ]
    d_5 = d_5[
        [
            "Insertion_datetime",
            "Bulletin",
            "Station",
            "Predicted_datetime",
            "Delay_in_sec",
        ]
    ]
    d_5.Delay_in_sec = round((d_5.Delay_in_sec / 60).astype(int))
    d_5.columns = [
        "Insertion_datetime",
        "Bulletin",
        "Station",
        "Predicted_datetime",
        "Delay_in_minutes",
    ]
    d_5.sort_values(by=["Station"], inplace=True)

    aux_df = df.loc[df.Correction == "No Correction"]
    aux1 = pd.DataFrame(aux_df.groupby(["Station"]).size())
    aux1 = aux1.reset_index()
    aux1.columns = ["Station", "Received"]
    aux2 = df.loc[df.Delayed == 1].groupby(["Station"]).size()
    aux2 = aux2.reset_index()
    aux2.columns = ["Station", "Delayed"]
    sec_sheet = pd.merge(aux1, aux2, on="Station", how="outer")
    sec_sheet.loc[np.isnan(sec_sheet.Delayed), "Delayed"] = 0
    sec_sheet.Delayed = sec_sheet.Delayed.astype(int)
    sec_sheet["Percentages"] = round((sec_sheet.Delayed / sec_sheet.Received) * 100, 1)
    sec_sheet["Reason"] = " "
    sec_sheet["Contact Name"] = " "
    sec_sheet = sec_sheet.loc[
        (sec_sheet.Station.astype(str).str[0] == "L")
        & (sec_sheet.Station.astype(str).str[1] == "G")
    ]
    sec_sheet_row = pd.DataFrame(
        {
            "Station": "SUM",
            "Received": sec_sheet.Received.sum(),
            "Delayed": sec_sheet.Delayed.sum(),
            "Percentages": "",
            "Reason": "",
            "Contact Name": "",
        },
        index=[0],
    )
    sec_sheet = pd.concat([sec_sheet, sec_sheet_row], ignore_index=True)
    #########

    # Write and save final file
    writer = pd.ExcelWriter(target_pth + target_title)
    d_5.to_excel(writer, sheet_name="Delay Reason")
    sec_sheet.to_excel(writer, sheet_name="Summaries")
    writer.close()
    msg_forthebox = "Το αρχείο excel δημιουργήθηκε επιτυχημένα. Παρακαλώ πατήστε το ΟΚ"

# db process
socket_dict = dict()
transistor = 10
hour = 0
for index in range(1, 49):
    key = "s0" + str(index) if len(str(index)) == 1 else "s" + str(index)
    hr = "0" + str(hour) if hour < 10 else str(hour)
    if transistor % 2 == 0:
        val = [hr + ":" + "00", hr + ":" + "10", hr + ":" + "20"]

    else:
        val = [hr + ":" + "30", hr + ":" + "40", hr + ":" + "50"]
        if index > 1:
            hour += 1
    socket_dict[key] = val
    transistor += 1
sock_values = list(socket_dict.values())

# inserts into table "metar reporting"
for kl in list(df.Station.unique()):
    aux_df = df.loc[df.Station == kl]
    aux_list = list(np.repeat(-1, 50))
    aux_list[0] = str(aux_df.iloc[0, 3]).split(" ")[0]
    aux_list[1] = kl
    messages_received_1 = list(aux_df.Predicted_datetime.astype(str))
    messages_received_2 = [i.split(" ")[1][:5] for i in messages_received_1]
    for index, i in enumerate(messages_received_2):
        loceitio = [indx for indx, val in enumerate(sock_values) if i in val]
        if len(loceitio) == 0:
            continue
        loceitio = loceitio[0]
        if aux_df.iloc[index, 7] == 1:
            aux_list[loceitio + 2] = round(aux_df.iloc[index, 4] / 60)
        else:
            aux_list[loceitio + 2] = 0
    new_aux_list = [aux_list[0].replace("-", "") + aux_list[1]] + aux_list
    new_aux_list.append(aux_df.loc[aux_df.Correction != "CCA"].shape[0])
    new_aux_list.append(aux_df.loc[aux_df.Delayed == 1].shape[0])
    query_insert(str(new_aux_list).strip("[]"))

# insert into table "delayed"
for ireal in range(d_5.shape[0]):
    first = str(d_5.iloc[ireal, 3]).replace("-", "").replace(":", "").replace(" ", "")
    second = str(d_5.iloc[ireal, 0]).replace("-", "").replace(":", "").replace(" ", "")
    third = d_5.iloc[ireal, 2]
    new_kathisterimena_id = first + second + third
    new_kathisterimena_list = list(d_5.iloc[ireal, :])
    new_kathisterimena = [new_kathisterimena_id] + new_kathisterimena_list
    query_insert_2(str(new_kathisterimena).strip("[]"))

messagebox.showinfo("D5", msg_forthebox)