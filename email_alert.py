import smtplib
from email.mime.text import MIMEText
import base64
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def send_email(track_id, violation_type,plate_text, speed,image_base64):
    sender = 'theerthahari2002@gmail.com'
    password = 'keaj jfgt ekrh cyhu'
    receiver = 'theerthahari2002@gmail.com'

    text = f"""\
    Traffic Violation Alert

    Track ID: {track_id}
    Violation: {violation_type}
    License Plate: {plate_text}
    """

    if isinstance(speed, (float, int)) and speed > 0:
        text += f"\nSpeed: {speed:.1f} km/h"

    msg = MIMEMultipart()
    msg['Subject'] = f"ALERT: {violation_type.upper()} "
    msg['From'] = sender
    msg['To'] = receiver

    msg.attach(MIMEText(text, 'plain'))


    try:
        image_data = base64.b64decode(image_base64)
        image = MIMEImage(image_data, name=f"violation_{track_id}.jpg")
        msg.attach(image)
    except Exception as e:
        print(f"[Email Error] Could not attach image: {e}")

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("Email sent.")
    except Exception as e:
        print(f"Error: {e}")