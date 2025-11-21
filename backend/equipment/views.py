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
import pandas as pd
from django.conf import settings

from .models import Dataset, Equipment
from .serializers import (
    DatasetSerializer, 
    DatasetDetailSerializer, 
    RegisterSerializer,
    LoginSerializer,
    UserSerializer
)
from .services import analyze_equipment_csv_from_uploaded_file, CSVParsingError, generate_ai_insights, AIGenerationError
from .pdf_utils import generate_pdf_response


# Auth stuff

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    """
    Handles user registration by validating input data and creating a new user account.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Public endpoint
    
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)

            if serializer.is_valid():
                result = serializer.save()
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
    Authenticates a user and returns an auth token.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Public endpoint
    
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                result = serializer.save()
                return Response(result, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'error': 'Login failed',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Invalidates the user's auth token to log them out.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def post(self, request):
        try:
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
    Retrieves the profile information for the currently authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadDatasetView(APIView):
    """
    Handles CSV file uploads, performs initial analysis, and stores the dataset.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def post(self, request):
        try:
            # Validate file presence
            file_obj = request.FILES.get("file")
            if not file_obj:
                return Response({
                    'error': 'No file uploaded',
                    'detail': 'Please provide a CSV file in the "file" field'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check file type
            if not file_obj.name.lower().endswith('.csv'):
                return Response({
                    'error': 'Invalid file type',
                    'detail': 'Only CSV files are allowed'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get name or create default
            name = request.data.get('name', f"Dataset {timezone.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Analyze CSV
            file_obj.seek(0)
            analysis_result = analyze_equipment_csv_from_uploaded_file(file_obj)
            
            # Reset pointer for saving
            file_obj.seek(0)
            
            # Create dataset record
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
                preview_rows=analysis_result['preview_rows']
            )
            
            # Create equipment records
            from .services import normalize_column_name
            try:
                # Try reading saved file
                if dataset.csv_file and hasattr(dataset.csv_file, 'path'):
                    df = pd.read_csv(dataset.csv_file.path)
                else:
                    # Fallback to uploaded file
                    file_obj.seek(0)
                    df = pd.read_csv(file_obj)
            except (ValueError, AttributeError, OSError, FileNotFoundError):
                df = None
            
            if df is not None:
                df.columns = [normalize_column_name(str(col)) for col in df.columns]
                
                # Create equipment objects
                eq_objects = []
                for _, row in df.iterrows():
                    # Skip empty rows
                    if pd.isna(row.get('equipment_name')) and pd.isna(row.get('type')):
                        continue
                        
                    eq_objects.append(Equipment(
                        dataset=dataset,
                        name=str(row.get('equipment_name', '')).strip() if not pd.isna(row.get('equipment_name')) else '',
                        type=str(row.get('type', '')).strip() if not pd.isna(row.get('type')) else '',
                        flowrate=float(row.get('flowrate', 0)) if not pd.isna(row.get('flowrate')) else 0.0,
                        pressure=float(row.get('pressure', 0)) if not pd.isna(row.get('pressure')) else 0.0,
                        temperature=float(row.get('temperature', 0)) if not pd.isna(row.get('temperature')) else 0.0
                    ))
                
                # Bulk create in batches
                if eq_objects:
                    batch_size = 1000
                    for i in range(0, len(eq_objects), batch_size):
                        batch = eq_objects[i:i + batch_size]
                        Equipment.objects.bulk_create(batch, ignore_conflicts=True)
            
            # Return dataset info
            detail_serializer = DatasetDetailSerializer(dataset, context={'request': request})
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
    # List datasets
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        # Get last 5 datasets
        return Dataset.objects.order_by('-uploaded_at')[:5]
    
    def list(self, request, *args, **kwargs):
        # Return array
        try:
            qs = self.get_queryset()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to fetch datasets',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetDetailView(RetrieveAPIView):
    # Get dataset details
    serializer_class = DatasetDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Dataset.objects.all()
    lookup_field = 'id'
    
    def get_object(self):
        # Get dataset or 404
        qs = self.get_queryset()
        obj = get_object_or_404(qs, id=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj
    
    def retrieve(self, request, *args, **kwargs):
        # Handle errors
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Failed to fetch dataset details',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetPDFReportView(APIView):
    # Generate PDF report
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request, pk):
        # Generate PDF
        try:
            dataset = get_object_or_404(Dataset, id=pk)
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


class DatasetAnalyzeView(APIView):
    # Generate AI insights
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request, pk):
        # Get AI analysis
        try:
            dataset = get_object_or_404(Dataset, id=pk)
            
            # Prepare data for AI
            summary = {
                'total_count': dataset.total_count,
                'avg_flowrate': dataset.avg_flowrate,
                'avg_pressure': dataset.avg_pressure,
                'avg_temperature': dataset.avg_temperature,
                'type_distribution': dataset.type_distribution or {}
            }
            
            # Generate insights
            insights = generate_ai_insights(summary)
            
            return Response({
                'insights': insights
            }, status=status.HTTP_200_OK)
            
        except AIGenerationError as e:
            return Response({
                'error': 'AI generation failed',
                'detail': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        except Exception as e:
            import traceback
            error_detail = str(e)
            if settings.DEBUG:
                error_detail += f"\n{traceback.format_exc()}"
            return Response({
                'error': 'Analysis failed',
                'detail': error_detail
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
