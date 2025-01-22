"""
URL configuration for earnexam project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/',include('users.urls')),
    path('api/questions/',include('questions.urls')),
    path('api/exams/',include('exams.urls')),
    path('api/quizzes/',include('quizzes.urls')),
    path('api/results/',include('results.urls')),
    path('api/wallets/',include('wallets.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/contests/', include('contests.urls')),
    path('api/friendship/', include('friendship.urls')),
    path('api/blogs/', include('blogs.urls')),
    path('api/ebooks/', include('ebooks.urls')),
    path('api/StudyMaterial/', include('StudyMaterial.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)