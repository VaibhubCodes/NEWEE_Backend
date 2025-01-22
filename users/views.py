import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, Teacher, Student
from .serializers import RegisterSerializer, UserSerializer, TeacherSerializer, StudentSerializer
from django.conf import settings
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response(serializer.errors, status=400)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        data = request.data

        # Update user fields
        user.name = data.get("name", user.name)
        user.phone = data.get("phone", user.phone)
        user.pan_number = data.get("pan_number", user.pan_number)
        user.upi_id = data.get("upi_id", user.upi_id)
        user.aadhar_number = data.get("aadhar_number", user.aadhar_number)
        user.latitude = data.get("latitude", user.latitude)
        user.longitude = data.get("longitude", user.longitude)
        user.save()

        # Handle role-specific updates
        if user.role == "Teacher":
            teacher_data = {
                "school_id": data.get("school_id"),
                "location": data.get("location"),
            }
            Teacher.objects.update_or_create(user=user, defaults=teacher_data)

        elif user.role == "Student":
            student_data = {
                "school_id": data.get("school_id"),
                "address": data.get("address"),
                "date_of_birth": data.get("date_of_birth") or None,
                "location": data.get("location"),
                "class_name": data.get("class_name"),
            }
            Student.objects.update_or_create(user=user, defaults=student_data)

        return Response({"message": "Profile updated successfully"}, status=200)


class UserListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class StudentFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        class_name = request.query_params.get('class_name')
        school_id = request.query_params.get('school_id')
        location = request.query_params.get('location')

        students = Student.objects.all()

        if class_name:
            students = students.filter(class_name=class_name)
        if school_id:
            students = students.filter(school_id=school_id)
        if location:
            students = students.filter(location=location)

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


class UpdateLocationView(APIView):
    """
    View to update the user's location using Google Geocoding API.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if not latitude or not longitude:
            return Response({"error": "Latitude and longitude are required."}, status=400)

        try:
            # Use the Google Geocoding API to fetch the location address
            google_maps_api_key = settings.GOOGLE_MAPS_API_KEY
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={google_maps_api_key}"

            response = requests.get(geocode_url)
            if response.status_code != 200:
                return Response({"error": "Failed to fetch location from Google API."}, status=500)

            geocode_data = response.json()
            if geocode_data.get("status") != "OK":
                return Response({"error": "Failed to fetch location details."}, status=500)

            location_address = geocode_data["results"][0]["formatted_address"]

            # Update the user's location
            user.latitude = latitude
            user.longitude = longitude
            user.location = location_address
            user.save()

            return Response(
                {
                    "message": "Location updated successfully.",
                    "latitude": user.latitude,
                    "longitude": user.longitude,
                    "location": user.location,
                },
                status=200,
            )

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)
