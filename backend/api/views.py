from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse

from .models import Dataset
from .utils import analyze_csv, generate_pdf_latex


class UploadCSV(APIView):
    def post(self, request):
        file = request.FILES.get("file")

        summary = analyze_csv(file)

        dataset = Dataset.objects.create(
            name=file.name,
            summary=summary
        )

        # Keep only last 5 datasets
        old = Dataset.objects.all().order_by('-uploaded_at')[5:]
        for d in old:
            d.delete()

        response_data = summary.copy()
        response_data['id'] = dataset.id

        return Response(response_data)


class History(APIView):
    def get(self, request):
        datasets = Dataset.objects.all().order_by('-uploaded_at')

        return Response([
            {
                "id": d.id,
                "name": d.name,
                "uploaded_at": d.uploaded_at,
                "total": d.summary["total_equipment"]
            }
            for d in datasets
        ])


class DownloadReport(APIView):
    def get(self, request, id):
        dataset = Dataset.objects.get(id=id)
        pdf_path = generate_pdf_latex(dataset.summary)

        return FileResponse(
            open(pdf_path, "rb"),
            as_attachment=True,
            filename="equipment_report.pdf"
        )
