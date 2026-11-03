from django.test import TestCase,Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Ticket,FAQ,Message
from .services import extract
from unittest.mock import patch
class WorkflowTests(TestCase):
    def setUp(self):
        self.student=User.objects.create_user('student',password='test-password')
        self.other=User.objects.create_user('other',password='test-password')
        self.staff=User.objects.create_user('staff',password='test-password',is_staff=True)
        self.client=APIClient()
        self.client.force_authenticate(self.student)
        self.payload={'title':'Wi-Fi broken','category':'Network','location':'Hostel Block B, Room 204','description':'Wi-Fi has been down since yesterday.'}
    @patch.dict('os.environ',{'OPENAI_API_KEY':''})
    def test_intake_followup_confirmation_and_duplicates(self):
        first=self.client.post('/api/conversation',{'text':'Wi-Fi nahi chal raha'},format='json')
        self.assertNotIn('draft',first.data)
        second=self.client.post('/api/conversation',{'text':'Hostel block B room 204'},format='json')
        self.assertEqual(second.data['draft']['location'],'Hostel Block B, Room 204')
        self.assertEqual(Ticket.objects.count(),0)
        created=self.client.post('/api/tickets',second.data['draft'],format='json')
        self.assertEqual(created.status_code,201)
        self.assertEqual(created.data['status'],'Open')
        third=self.client.post('/api/conversation',{'text':'wifi broken in block B room 204'},format='json')
        self.assertEqual(third.data['duplicate_count'],1)
        self.assertEqual(Message.objects.count(),6)
    def test_permissions_status_and_history(self):
        own=Ticket.objects.create(owner=self.student,**self.payload)
        other=Ticket.objects.create(owner=self.other,**self.payload)
        self.assertEqual(len(self.client.get('/api/tickets').data),1)
        self.assertEqual(self.client.get(f'/api/tickets/{other.pk}').status_code,404)
        self.assertEqual(self.client.patch(f'/api/tickets/{own.pk}',{'status':'Resolved'}).status_code,403)
        self.client.force_authenticate(self.staff)
        self.assertEqual(len(self.client.get('/api/tickets').data),2)
        result=self.client.patch(f'/api/tickets/{own.pk}',{'status':'Resolved','note':'Fixed access point'},format='json')
        self.assertEqual(result.status_code,200)
        self.assertIn('Fixed access point',result.data['updates'][0]['message'])
        self.client.force_authenticate(self.student)
        reply=self.client.post('/api/conversation',{'text':f'status of ticket {own.pk}'},format='json')
        self.assertIn('Resolved',reply.data['reply'])
        reply=self.client.post('/api/conversation',{'text':f'status of ticket {other.pk}'},format='json')
        self.assertIn('could not find',reply.data['reply'])
    def test_validation_and_unauthenticated_access(self):
        self.assertEqual(self.client.post('/api/tickets',{},format='json').status_code,400)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/tickets').status_code,403)
    @patch.dict('os.environ',{'OPENAI_API_KEY':''})
    def test_transcription_validates_audio_without_api_key(self):
        self.assertEqual(self.client.post('/api/transcribe').status_code,400)
    def test_faq_grounding_and_upload_permissions(self):
        FAQ.objects.create(title='College handbook',content='Administration office hours are 9 AM to 5 PM.')
        reply=self.client.post('/api/conversation',{'text':'When are administration office hours?'},format='json')
        self.assertIn('College handbook',reply.data['reply'])
        self.assertEqual(self.client.post('/api/faq').status_code,403)
    def test_login_csrf(self):
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.post('/api/login',data='{}',content_type='application/json').status_code,403)
        c.get('/')
        token=c.cookies['csrftoken'].value
        r=c.post('/api/login',data='{"username":"student","password":"test-password"}',content_type='application/json',HTTP_X_CSRFTOKEN=token)
        self.assertEqual(r.status_code,200)
