import smtplib
import os
from email.mime.text import MIMEText
from langchain.agents import create_react_agent, AgentExecutor, AgentType
from langchain.tools import Tool
subject = "Email Subject"
# body = "Hi from jyoti"
sender = os.environ['DOMAIN_EMAIL']
# recipients = ["aashishsamarth11@gmail.com"]
password = os.environ['DOMAIN_PASSWORD']


def send_email(recipient):
    subject = "Email Subject"
    body = "Hi from palbot"
    sender = os.environ['DOMAIN_EMAIL']
    # recipients = "aashishsamarth11@gmail.com"
    password = os.environ['DOMAIN_PASSWORD']
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    recipients = [recipient]
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    # print("Message sent!")
    return 'Message sent to the user successfully!'

# recipient = 'aashishsamarth11@gmail.com'

tool_desc = '''Sends an email to a specified recipient.

               This tool takes an email address as input and sends a pre-defined email. The email's subject and body are fixed.

               Input: The email address of the recipient.

               Output: A confirmation message indicating that the email was sent successfully.'''


email_tool = Tool(
    name='email_tool',
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    func=lambda recipient: send_email(recipient),
    description=tool_desc
)
# send_email(recipient)

