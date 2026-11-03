import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
DEBUG=os.getenv('DJANGO_DEBUG','1')=='1'
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','development-only-change-this-key')
if not DEBUG and SECRET_KEY.startswith('development-only'): raise RuntimeError('Set DJANGO_SECRET_KEY')
ALLOWED_HOSTS=os.getenv('DJANGO_ALLOWED_HOSTS','localhost,127.0.0.1,testserver').split(',')
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.staticfiles','rest_framework','desk']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware']
ROOT_URLCONF='voicedesk.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
if os.getenv('POSTGRES_DB'):
    DATABASES['default']={'ENGINE':'django.db.backends.postgresql','NAME':os.environ['POSTGRES_DB'],'USER':os.getenv('POSTGRES_USER','postgres'),'PASSWORD':os.getenv('POSTGRES_PASSWORD',''),'HOST':os.getenv('POSTGRES_HOST','localhost'),'PORT':os.getenv('POSTGRES_PORT','5432')}
STATIC_URL='/static/'
STATICFILES_DIRS=[BASE_DIR/'static']
STATIC_ROOT=BASE_DIR/'staticfiles'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
USE_TZ=True
TIME_ZONE='Asia/Kolkata'
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG
DATA_UPLOAD_MAX_MEMORY_SIZE=26*1024*1024
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated']}

# Development edits must not reuse cached templates with newer static assets.
if DEBUG:
    TEMPLATES[0]['APP_DIRS']=False
    TEMPLATES[0]['OPTIONS']={'loaders':['django.template.loaders.filesystem.Loader','django.template.loaders.app_directories.Loader']}
