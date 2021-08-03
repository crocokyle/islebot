from email.message import EmailMessage
import smtplib
import getpass

message = EmailMessage()

sender = "me@example.com"
recipient = "you@example.com"

message['From'] = sender
message['To'] = recipient
message['Subject'] = 'Greetings from {} to {}!'.format(sender, recipient)

body = """Hey there!

I'm learning to send emails using Python!"""
message.set_content(body)

print(message)

mail_server = smtplib.SMTP_SSL('smtp.example.com')
mail_pass = getpass.getpass('Password? ')
mail_server.login(sender, mail_pass)
 
mail_server.send_message(message)
 
mail_server.quit() # Close the connection to the mail server