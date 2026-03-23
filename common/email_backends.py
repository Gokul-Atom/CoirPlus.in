from django.core.mail.backends.base import BaseEmailBackend
from .models import ScheduledMessage
from django.utils import timezone


class CustomEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for message in email_messages:
            # Get HTML body
            html_body = None
            if message.content_subtype == 'html':
                html_body = message.body
            else:
                # Check alternatives for text/html
                for alt in message.alternatives:
                    if alt[1] == 'text/html':
                        html_body = alt[0]
                        break

            ScheduledMessage.objects.create(
                subject=message.subject,
                text_body=message.body if message.content_subtype != 'html' else '',
                html_body=html_body if html_body else message.body.replace("\n", "<br"),
                to_emails=', '.join(message.to),
                scheduled_time=timezone.now(),  # Set if you pass scheduling info
                sent_at=None,
            )
        return len(email_messages)
