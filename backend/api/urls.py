from django.urls import path
from .views import UploadCSV, History, DownloadReport
from .csrf import get_csrf

urlpatterns = [
    path("upload/", UploadCSV.as_view()),
    path("history/", History.as_view()),
    path("report/<int:id>/", DownloadReport.as_view()),
    path("csrf/", get_csrf),
]
