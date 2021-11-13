from django.urls import path
from fileupload.views import home,reportlab_view,error
from django.conf.urls.static import static 
from django.conf import settings

from django.views.static import serve
from django.conf.urls import url

urlpatterns = [
    path('',home,name="home"),
    path('error/',error,name="error"),
    path('download/', reportlab_view, name="download_report"),
    # url(r'^media/(?P<path>.*)$', serve,{'document_root':       settings.MEDIA_ROOT}), 
    # url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    
