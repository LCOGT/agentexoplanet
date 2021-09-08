from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core import mail
from django.template.loader import get_template


class Command(BaseCommand):
    help = 'Send Goodbye email to all users'

    def handle(self, *args, **options):
        users = User.objects.filter(id__gt=113)
        # users = [User.objects.get(username='zemogle')]
        fromemail = 'no-reply@lco.global'
        subject = "Agent Exoplanet coming to an end"
        htmly = get_template('agentex/goodbye_email.txt')
        total = users.count()
        start = 0
        end = 100
        with mail.get_connection() as connection:
            while start < total:
                userbatch = users[start:end]
                for user in userbatch:
                    body = htmly.render({ 'first_name': user.first_name })
                    msg = mail.EmailMessage(
                        subject, body, fromemail, [user.email],
                        connection=connection,
                    )
                    msg.content_subtype = "html"
                    try:
                        msg.send()
                        self.stdout.write(f'Emailed {user.email} - {user.id}')
                    except Exception as e:
                        self.stderr.write(f'Failed {user.email} - {user.id} with {e}')
                start = end +1
                end += 100
                if end > total:
                    end = total
