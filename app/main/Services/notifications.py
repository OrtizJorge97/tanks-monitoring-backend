import time
import smtplib

from app import mail_user, mail_password, smtp_server_string, port

def send_tank_alert_mail(to_mails, tanks_parameters, current_tank_values):
    to_emails = [mail['email'] for mail in to_mails]
    string_alert_list = []

    print("-------TO MAILS------------------")
    print(to_mails)
    print("---------------TANKS PARAMETERS--------------")
    print(tanks_parameters)
    print("--------------CURRENT TANK VALUES----------------")
    print(current_tank_values)

    for tank_parameters in tanks_parameters:
        tank_current_index = current_tank_values['id'].index(tank_parameters['tank_name'])
        measure_type = tank_parameters['measure_type']
        parameter_min_value = tank_parameters['tank_min_value']
        parameter_max_value = tank_parameters['tank_max_value']

        current_value = current_tank_values[measure_type][tank_current_index]
        if current_value < parameter_min_value:
            string_alert_list.append(f"Tank {tank_parameters['tank_name']} is less than inferior category {measure_type} with current value of {current_value} bound value {parameter_min_value} at {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(current_tank_values['timestamp'][tank_current_index]))}\n")
        elif current_value > parameter_max_value:
            string_alert_list.append(f"Tank {tank_parameters['tank_name']} is greater than superior category {measure_type} with current value of {current_value} bound value {parameter_max_value} at {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(current_tank_values['timestamp'][tank_current_index]))}\n")
        
    print("---------PRINTING STRING MESSAGES------------")
    print(string_alert_list)
    print("----------PRINTING LENGTH MESSAGES--------------")
    print(len(string_alert_list))

    if len(string_alert_list):
        gmail_user = mail_user
        gmail_password = mail_password

        sent_from = gmail_user
        to = to_emails
        subject = 'TANKS ALERT MESSAGE: BOUNDS SURPASSED! - SUMMARY'
        body = "".join(string_alert_list)
        print("---------PRINTING MAIL BODY--------------")
        print(body)
        email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, body)

        try:
            smtp_server = smtplib.SMTP_SSL(smtp_server_string, port)
            smtp_server.ehlo()
            smtp_server.login(gmail_user, gmail_password)
            smtp_server.sendmail(sent_from, to, email_text)
            smtp_server.close()
            print ("Email sent successfully!")
        except Exception as ex:
            print ("Something went wrong….",ex)

def send_email(to_emails, subject, body):
    gmail_user = mail_user
    gmail_password = mail_password

    sent_from = gmail_user
    to = to_emails
    subject = subject
    body = body
    print("---------PRINTING MAIL BODY--------------")
    print(body)
    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL(smtp_server_string, port)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)