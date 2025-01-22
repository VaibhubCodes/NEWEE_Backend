from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import StudyMaterial, Enrollment
from .serializers import StudyMaterialSerializer, EnrollmentSerializer

class StudyMaterialListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        study_materials = StudyMaterial.objects.all()
        serializer = StudyMaterialSerializer(study_materials, many=True)
        return Response(serializer.data)

class StudyMaterialDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, material_id):
        try:
            study_material = StudyMaterial.objects.get(id=material_id)
            serializer = StudyMaterialSerializer(study_material)
            return Response(serializer.data)
        except StudyMaterial.DoesNotExist:
            return Response({"error": "Study material not found."}, status=404)

class EnrollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, material_id):
        try:
            study_material = StudyMaterial.objects.get(id=material_id)
            if study_material.is_paid and not request.data.get("payment_status") == "completed":
                return Response({"error": "Payment is required for this course."}, status=400)
            
            enrollment, created = Enrollment.objects.get_or_create(
                student=request.user, 
                study_material=study_material, 
                defaults={'payment_status': request.data.get("payment_status", "pending")}
            )

            if created:
                return Response({"message": "Enrolled successfully."}, status=201)
            return Response({"message": "Already enrolled."}, status=200)
        except StudyMaterial.DoesNotExist:
            return Response({"error": "Study material not found."}, status=404)
