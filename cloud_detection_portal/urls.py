"""
URL configuration for cloud_detection_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Health check endpoint for load balancers and monitoring
@csrf_exempt
def health_check(request):
    """Simple health check endpoint for Compute Engine"""
    return JsonResponse({
        'status': 'healthy',
        'environment': settings.ENVIRONMENT,
        'debug': settings.DEBUG
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cloud_detection.urls')),
    path('health/', health_check, name='health_check'),  # Health check endpoint
]

# Serve media files during development and production
if settings.DEBUG or settings.ENVIRONMENT == 'production':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
