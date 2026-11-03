from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from desk.models import Ticket,Update,FAQ
class Command(BaseCommand):
    help='Create local demo accounts and example complaints. Never run on a public deployment.'
    @transaction.atomic
    def handle(self,*args,**options):
        student,created=User.objects.get_or_create(username='student',defaults={'first_name':'Aarav Sharma'})
        if created: student.set_password('VoiceDesk123!'); student.save()
        staff,created=User.objects.get_or_create(username='staff',defaults={'first_name':'Priya Mehta','is_staff':True})
        if created: staff.set_password('VoiceDesk123!'); staff.save()
        if not Ticket.objects.filter(owner=student).exists():
            data=[('Wi-Fi keeps disconnecting','Network','Hostel Block B, Room 204','In progress'),('Leaking tap in the washroom','Maintenance','Hostel Block B, Floor 2','Open'),('Projector display is blurry','Classroom','Classroom 302','Resolved'),('Request for a bonafide certificate','Administration','Administration Office','Resolved')]
            for n,(title,cat,loc,status) in enumerate(data,101):
                t=Ticket.objects.create(id=n,owner=student,title=title,category=cat,location=loc,description=title+'. Please help resolve this campus issue.',status=status)
                Update.objects.create(ticket=t,message='Complaint registered and added to the campus support queue.')
                if status=='In progress': Update.objects.create(ticket=t,message='The IT team is checking the access point in Block B.')
                if status=='Resolved': Update.objects.create(ticket=t,message='The support team has resolved this request.')
            from django.core.management.color import no_style
            from django.db import connection
            for sql in connection.ops.sequence_reset_sql(no_style(),[Ticket]):
                with connection.cursor() as cursor: cursor.execute(sql)
        if not FAQ.objects.exists():
            FAQ.objects.create(title='Demo campus handbook',content='How do I connect to campus Wi-Fi?\nSelect Campus-Student and sign in with your college username and password. If you cannot connect, report a Network complaint with your block and room. These are sample instructions; staff should upload the real college FAQ.')
            FAQ.objects.create(title='Demo campus handbook',content='When is the administration office open?\nSample office hours are Monday to Friday, 9:00 AM to 5:00 PM. Ask your college to confirm its actual hours.')
            FAQ.objects.create(title='Demo campus handbook',content='How can I check my complaint status?\nOpen My complaints and select a ticket, or ask the voice assistant “What is the status of ticket 101?”')
        self.stdout.write(self.style.SUCCESS('Demo ready: student / staff — password VoiceDesk123!'))
