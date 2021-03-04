from flask_mail import Mail, Message
from .celery_creator import celery

mail = Mail()


@celery.task()
def send_notification_email(users_list, fork_category):
    """Sends an email to a list of users, subscribed to some fork category."""
    for user in users_list:
        user_email = user.get('user_email')
        msg = Message('New fork added!',
                      sender='fork_project@gmail.com',
                      recipients=user_email.split())
        msg.body = f"""Hello, {user_email},
New fork was added to {fork_category}
"""
    mail.send(msg)
