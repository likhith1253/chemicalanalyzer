from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Dataset, Equipment
from .serializers import (
    DatasetSerializer, 
    DatasetDetailSerializer, 
    RegisterSerializer,
    LoginSerializer,
    UserSerializer
)
from .services import analyze_equipment_csv_from_uploaded_file, CSVParsingError
import pandas as pd
from .pdf_utils import generate_pdf_response
from django.conf import settings


# Authentication Views

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    """
    User registration endpoint.
    
    POST /api/auth/register/
    Accepts: username, password (email and password_confirm optional)
    Returns EXACTLY: { "token": "<token>", "username": "<username>" }
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No authentication required
    
    def post(self, request):
        """
        Register a new user and return token.
        """
        try:
            serializer = RegisterSerializer(data=request.data)

            if serializer.is_valid():
                result = serializer.save()
                # Return EXACTLY {token, username} as specified
                return Response(result, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Registration failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    User login endpoint.
    
    POST /api/auth/login/
    Accepts: username, password
    Returns EXACTLY: { "token": "<token>", "username": "<username>" }
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No authentication required
    
    def post(self, request):
        """
        Authenticate user and return token.
        """
        try:
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                result = serializer.save()
                # Return EXACTLY {token, username} as specified
                return Response(result, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'error': 'Login failed',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    User logout endpoint.
    
    POST /api/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def post(self, request):
        """
        Delete user's authentication token.
        """
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({
                'message': 'No active token found'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    Get current user profile.
    
    GET /api/auth/profile/
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        """
        Return current user's profile information.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadDatasetView(APIView):
    """
    Upload and analyze a CSV file containing equipment data.
    
    POST /api/upload/
    Requires TokenAuthentication
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def post(self, request):
        """
        Upload CSV file, analyze it, and save as a dataset.
        
        Request body: multipart/form-data with 'file' field
        Optional: 'name' field for custom dataset name
        """
        try:
            # Validate file upload - use request.FILES.get("file")
            file_obj = request.FILES.get("file")
            if not file_obj:
                return Response({
                    'error': 'No file uploaded',
                    'detail': 'Please provide a CSV file in the "file" field'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate file extension
            if not file_obj.name.lower().endswith('.csv'):
                return Response({
                    'error': 'Invalid file type',
                    'detail': 'Only CSV files are allowed'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get optional name
            name = request.data.get('name', f"Dataset {timezone.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Analyze the uploaded CSV file
            file_obj.seek(0)
            analysis_result = analyze_equipment_csv_from_uploaded_file(file_obj)
            
            # Reset file pointer again for saving
            file_obj.seek(0)
            
            # Create dataset with the uploaded file
            dataset = Dataset.objects.create(
                name=name,
                original_filename=file_obj.name,
                uploaded_by=request.user,
                csv_file=file_obj,
                total_count=analysis_result['total_count'],
                avg_flowrate=analysis_result['avg_flowrate'],
                avg_pressure=analysis_result['avg_pressure'],
                avg_temperature=analysis_result['avg_temperature'],
                type_distribution=analysis_result['type_distribution'],
                preview_rows=analysis_result['preview_rows']  # Store preview rows
            )
            
            # Create equipment records from all rows in the CSV (optional, for PDF reports)
            from .services import normalize_column_name
            try:
                # Try to read from the saved file
                if dataset.csv_file and hasattr(dataset.csv_file, 'path'):
                    df = pd.read_csv(dataset.csv_file.path)
                else:
                    # Fallback: read from uploaded file
                    file_obj.seek(0)
                    df = pd.read_csv(file_obj)
            except (ValueError, AttributeError, OSError, FileNotFoundError):
                # If file reading fails, skip equipment creation
                df = None
            
            if df is not None:
                df.columns = [normalize_column_name(str(col)) for col in df.columns]
                
                # Create equipment records from all rows
                equipment_objects = []
                for _, row in df.iterrows():
                    # Skip rows with missing required fields
                    if pd.isna(row.get('equipment_name')) and pd.isna(row.get('type')):
                        continue
                        
                    equipment_objects.append(Equipment(
                        dataset=dataset,
                        name=str(row.get('equipment_name', '')).strip() if not pd.isna(row.get('equipment_name')) else '',
                        type=str(row.get('type', '')).strip() if not pd.isna(row.get('type')) else '',
                        flowrate=float(row.get('flowrate', 0)) if not pd.isna(row.get('flowrate')) else 0.0,
                        pressure=float(row.get('pressure', 0)) if not pd.isna(row.get('pressure')) else 0.0,
                        temperature=float(row.get('temperature', 0)) if not pd.isna(row.get('temperature')) else 0.0
                    ))
                
                # Bulk create equipment records in batches to avoid memory issues
                if equipment_objects:
                    batch_size = 1000
                    for i in range(0, len(equipment_objects), batch_size):
                        batch = equipment_objects[i:i + batch_size]
                        Equipment.objects.bulk_create(batch, ignore_conflicts=True)
            
            # Return the detailed dataset information
            detail_serializer = DatasetDetailSerializer(dataset, context={'request': request})
            
            # Return summary + preview_rows as specified
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
            
        except CSVParsingError as e:
            return Response({
                'error': 'CSV parsing failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            import traceback
            error_detail = str(e)
            if settings.DEBUG:
                error_detail += f"\n{traceback.format_exc()}"
            return Response({
                'error': 'Upload failed',
                'detail': error_detail
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetListView(ListAPIView):
    """
    List the last 5 datasets with summary information.
    
    GET /api/datasets/
    Requires TokenAuthentication
    Returns: Array of dataset summaries (last 5, most recent first)
    """
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        """
        Return the last 5 datasets ordered by upload date (most recent first).
        """
        return Dataset.objects.order_by('-uploaded_at')[:5]
    
    def list(self, request, *args, **kwargs):
        """
        Override to return array directly (not paginated).
        """
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to fetch datasets',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetDetailView(RetrieveAPIView):
    """
    Get detailed information about a specific dataset including preview rows.
    
    GET /api/datasets/<id>/
    Requires TokenAuthentication
    """
    serializer_class = DatasetDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Dataset.objects.all()
    lookup_field = 'id'
    
    def get_object(self):
        """
        Get dataset object or return 404.
        """
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj
    
    def retrieve(self, request, *args, **kwargs):
        """
        Override to handle errors gracefully.
        """
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Failed to fetch dataset details',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetPDFReportView(APIView):
    """
    Generate and return a PDF report for a specific dataset.
    
    GET /api/datasets/<id>/report/pdf/
    Requires TokenAuthentication
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request, pk):
        """
        Generate PDF report for the specified dataset.
        
        Returns PDF file as attachment with filename: dataset_<id>_report.pdf
        """
        try:
            dataset = get_object_or_404(Dataset, id=pk)
            
            # Generate PDF response using the utility function
            return generate_pdf_response(dataset)
            
        except Exception as e:
            import traceback
            error_detail = str(e)
            if settings.DEBUG:
                error_detail += f"\n{traceback.format_exc()}"
            return Response({
                'error': 'PDF generation failed',
                'detail': error_detail
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
