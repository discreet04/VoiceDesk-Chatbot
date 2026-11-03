import os,re,json
from django.shortcuts import render,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_protect
from django.views.decorators.http import require_POST
from django.db import transaction
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Ticket,Update,Message,FAQ,CATEGORIES,STATUSES
from .services import extract
@ensure_csrf_cookie
def index(request): return render(request,'index.html')
def user_data(u): return {'name':u.first_name or u.username,'username':u.username,'staff':u.is_staff}
@api_view(['GET'])
@permission_classes([AllowAny])
def session(request): return Response({'user':user_data(request.user) if request.user.is_authenticated else None,'ai_enabled':bool(os.getenv('OPENAI_API_KEY'))})
@require_POST
@csrf_protect
def sign_in(request):
    try: d=json.loads(request.body)
    except ValueError: return JsonResponse({'error':'Invalid request'},status=400)
    u=authenticate(request,username=d.get('username'),password=d.get('password'))
    if not u: return JsonResponse({'error':'Username or password is incorrect.'},status=400)
    login(request,u)
    return JsonResponse({'user':user_data(u)})
@api_view(['POST'])
def sign_out(request):
    logout(request)
    return Response({'ok':True})
def visible(u): return Ticket.objects.all() if u.is_staff else Ticket.objects.filter(owner=u)
def serialize(t):
    return {'id':t.pk,'title':t.title,'category':t.category,'location':t.location,'description':t.description,'status':t.status,'priority':t.priority,'created_at':t.created_at.isoformat(),'updated_at':t.updated_at.isoformat(),'owner':t.owner.first_name or t.owner.username,'updates':[{'message':u.message,'created_at':u.created_at.isoformat()} for u in t.updates.order_by('-created_at')]}
@api_view(['GET','POST'])
def tickets(request):
    if request.method=='GET': return Response([serialize(t) for t in visible(request.user).order_by('-created_at')])
    d=request.data
    if d.get('category') not in CATEGORIES or any(not isinstance(d.get(k),str) or not d[k].strip() for k in ['title','location','description']): return Response({'error':'Confirm a title, category, location and description.'},status=400)
    if len(d['title'])>160 or len(d['location'])>160 or len(d['description'])>4000: return Response({'error':'Ticket details are too long.'},status=400)
    with transaction.atomic():
        t=Ticket.objects.create(owner=request.user,**{k:d[k].strip() for k in ['title','category','location','description']})
        Update.objects.create(ticket=t,message='Complaint registered and added to the campus support queue.')
    request.session.pop('draft',None)
    return Response(serialize(t),status=201)
@api_view(['GET','PATCH'])
def ticket_detail(request,pk):
    t=get_object_or_404(visible(request.user),pk=pk)
    if request.method=='PATCH':
        if not request.user.is_staff: return Response({'error':'Staff access required.'},status=403)
        status=request.data.get('status',t.status)
        note=request.data.get('note','')
        if status not in STATUSES or not isinstance(note,str) or len(note)>2000: return Response({'error':'Invalid status or note.'},status=400)
        with transaction.atomic():
            t.status=status
            t.save()
            Update.objects.create(ticket=t,message=f'{status}: {note}' if note.strip() else f'Status changed to {status}.')
    return Response(serialize(t))
@api_view(['GET','POST','DELETE'])
def conversation(request):
    if request.method=='GET': return Response(list(Message.objects.filter(owner=request.user).order_by('-id').values('role','content')[:30])[::-1])
    if request.method=='DELETE':
        request.session.pop('draft',None)
        return Response({'ok':True})
    text=request.data.get('text','')
    if not isinstance(text,str) or not text.strip() or len(text)>4000: return Response({'error':'Enter a message up to 4,000 characters.'},status=400)
    Message.objects.create(owner=request.user,role='user',content=text)
    low=text.lower()
    result={}
    if any(w in low for w in ['status','progress','स्थिति','update on','ticket #']):
        number=re.search(r'\d+',text)
        qs=visible(request.user)
        t=qs.filter(pk=int(number[0])).first() if number else qs.order_by('-created_at').first()
        reply=f'Ticket #{t.pk}: {t.title}. Status: {t.status}. '+(t.updates.last().message if t.updates.exists() else '') if t else 'I could not find that ticket in your account.'
    elif any(w in low for w in ['how ','when ','where ','faq','timing','hours','कैसे','कब']):
        tokens=set(re.findall(r'\w+',low))-{'how','the','is','a','i','what','where','when','do','can','to','for','are','of','and'}
        ranked=sorted([(len(tokens & set(re.findall(r'\w+',(f.title+' '+f.content).lower()))),f) for f in FAQ.objects.all()],key=lambda x:x[0],reverse=True)
        reply=(ranked[0][1].content+'\nSource: '+ranked[0][1].title) if ranked and ranked[0][0]>=2 else 'I couldn’t find a reliable answer in the college FAQ. Contact the administration office or describe an issue to create a ticket.'
    else:
        draft=extract(text,request.session.get('draft'))
        request.session['draft']=draft
        missing=[k for k in ['category','location'] if not draft.get(k)]
        if missing: reply='Could you tell me '+('what kind of issue this is (network, maintenance, classroom or administration)' if 'category' in missing else 'the location, including your block and room number')+'?'
        else:
            reply='I’ve prepared your complaint. Review the details below, then confirm to register your ticket.'
            result['draft']=draft
            result['duplicate_count']=Ticket.objects.filter(category=draft['category'],location__iexact=draft['location']).exclude(status='Resolved').count()
    Message.objects.create(owner=request.user,role='assistant',content=reply)
    return Response({'reply':reply,**result})
@api_view(['POST'])
def transcribe(request):
    audio=request.FILES.get('audio')
    if not audio or audio.size>24*1024*1024: return Response({'error':'Upload audio smaller than 24 MB.'},status=400)
    if not audio.name.lower().endswith(('.webm','.wav','.mp3','.m4a','.mp4','.ogg')): return Response({'error':'Unsupported audio format.'},status=400)
    try:
        import io
        from .local_audio import transcribe_audio
        return Response({'text':transcribe_audio(io.BytesIO(audio.read()))})
    except Exception: return Response({'error':'Local transcription failed. Please try again.'},status=502)

@api_view(['GET','POST'])
def faq(request):
    if request.method=='POST':
        if not request.user.is_staff: return Response({'error':'Staff access required.'},status=403)
        f=request.FILES.get('file')
        if not f or f.size>500000 or not f.name.lower().endswith(('.txt','.md')): return Response({'error':'Upload a UTF-8 .txt or .md FAQ under 500 KB.'},status=400)
        try: content=f.read().decode('utf-8')
        except UnicodeDecodeError: return Response({'error':'File must use UTF-8 encoding.'},status=400)
        for chunk in content.split('\n\n'):
            if chunk.strip(): FAQ.objects.create(title=f.name[:160],content=chunk.strip())
    return Response(list(FAQ.objects.values('id','title','content')))
