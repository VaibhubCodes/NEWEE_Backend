from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Ebook
from .serializers import EbookSerializer

class EbookListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ebooks = Ebook.objects.all()
        serializer = EbookSerializer(ebooks, many=True)
        return Response(serializer.data)

class EbookDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, ebook_id):
        try:
            ebook = Ebook.objects.get(id=ebook_id)
            serializer = EbookSerializer(ebook)
            return Response(serializer.data)
        except Ebook.DoesNotExist:
            return Response({"error": "Ebook not found."}, status=404)
