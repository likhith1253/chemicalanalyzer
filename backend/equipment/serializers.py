from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for individual equipment records."""
    
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'type', 'flowrate', 'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for dataset listing (without preview rows)."""
    
    uploaded_by = serializers.StringRelatedField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'original_filename',
            'uploaded_by',
            'uploaded_at',
            'total_count',
            'avg_flowrate',
            'avg_pressure',
            'avg_temperature',
            'type_distribution'
        ]


class DatasetDetailSerializer(DatasetSerializer):
    """Serializer for dataset details including preview rows."""
    
    preview_rows = serializers.SerializerMethodField()
    
    class Meta(DatasetSerializer.Meta):
        fields = DatasetSerializer.Meta.fields + ['preview_rows']
    
    def get_preview_rows(self, obj):
        """
        Get preview rows from the stored preview_rows field or generate from equipment records.
        """
        # First, try to use stored preview_rows
        if obj.preview_rows and len(obj.preview_rows) > 0:
            return obj.preview_rows
        
        # Fallback: generate from equipment records (limit to 100)
        equipment_data = obj.equipment.all()[:100]
        
        preview_data = []
        for equipment in equipment_data:
            preview_data.append({
                'equipment_name': equipment.name,
                'type': equipment.type,
                'flowrate': float(equipment.flowrate) if equipment.flowrate is not None else None,
                'pressure': float(equipment.pressure) if equipment.pressure is not None else None,
                'temperature': float(equipment.temperature) if equipment.temperature is not None else None
            })
        
        return preview_data


class DatasetUploadSerializer(serializers.Serializer):
    """Serializer for CSV upload validation."""
    
    file = serializers.FileField(
        required=True,
        help_text="CSV file containing equipment data"
    )
    name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Optional name for the dataset (defaults to timestamp)"
    )
    
    def validate_file(self, value):
        """
        Validate the uploaded file is a CSV file.
        """
        if not value.name.lower().endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        
        # Check file size (limit to 10MB)
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("File size must be less than 10MB.")
        
        return value


# Authentication Serializers

class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration. Returns exactly {token, username}."""
    
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password_confirm = serializers.CharField(write_only=True, required=False)
    
    def validate_username(self, value):
        """Validate username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    def validate(self, attrs):
        """
        Validate that passwords match if password_confirm is provided.
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password_confirm and password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match."})
        
        # Check if email already exists (if provided)
        email = attrs.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already exists."})
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user and return exactly {token, username}.
        """
        password_confirm = validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        email = validated_data.pop('email', '')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
            password=password
        )
        
        # Automatically create DRF token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return EXACTLY as specified: {token, username}
        return {
            'token': token.key,
            'username': user.username
        }


class LoginSerializer(serializers.Serializer):
    """Serializer for user login. Returns exactly {token, username}."""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        """
        Validate user credentials.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        
        # Store user for use in save()
        attrs['user'] = user
        return attrs
    
    def save(self):
        """
        Create token if missing and return exactly {token, username}.
        """
        user = self.validated_data['user']
        
        # Get or create token (create if missing)
        token, created = Token.objects.get_or_create(user=user)
        
        # Return EXACTLY as specified: {token, username}
        return {
            'token': token.key,
            'username': user.username
        }


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""
    
    token = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'token']
        read_only_fields = ['id', 'date_joined', 'token']
    
    def get_token(self, obj):
        """
        Get or create token for the user.
        """
        token, created = Token.objects.get_or_create(user=obj)
        return token.key
