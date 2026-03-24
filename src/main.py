import os
import subprocess
import smtplib
from email.mime.text import MIMEText

def scan_for_vulnerabilities():
    """Runs a security scan on the codebase and returns a list of found vulnerabilities."""
    try:
        output = subprocess.check_output(['safety', 'check'], universal_newlines=True)
        vulnerabilities = output.strip().split('\n')
        return vulnerabilities
    except subprocess.CalledProcessError as e:
        return [f'Error running security scan: {e}']

def send_alert(recipients, message):
    """Sends an email alert to the specified recipients."""
    msg = MIMEText(message)
    msg['Subject'] = 'Security Alert from GitSentinel'
    msg['From'] = 'alerts@gitsentinel.com'
    msg['To'] = ', '.join(recipients)

    with smtplib.SMTP('localhost') as smtp:
        smtp.send_message(msg)

def main():
    """Main entry point for the application."""
    recipients = os.environ.get('ALERT_RECIPIENTS', 'admin@example.com').split(',')
    vulnerabilities = scan_for_vulnerabilities()
    if vulnerabilities:
        message = '\n'.join(vulnerabilities)
        send_alert(recipients, message)
    else:
        print('No security vulnerabilities found.')

if __name__ == '__main__':
    main()