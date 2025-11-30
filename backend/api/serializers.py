from rest_framework import serializers
from .models import Entry, Exit, ActiveCar, Setting, User, Wallet, Transaction, UserPlate


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['id', 'plate', 'image_in', 'timestamp_in']


class ExitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exit
        fields = ['id', 'entry', 'plate', 'image_out', 'timestamp_out', 'duration_minutes', 'cost']


class ActiveCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveCar
        fields = ['entry', 'plate', 'timestamp_in']


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ['key', 'value']


class ParkingStatusSerializer(serializers.Serializer):
    """Serializer for parking status overview"""
    capacity = serializers.IntegerField()
    active_cars = serializers.IntegerField()
    free_slots = serializers.IntegerField()
    price_per_hour = serializers.IntegerField()


# Authentication Serializers

class UserSerializer(serializers.Serializer):
    """Serializer for user data (excludes sensitive information)"""
    id = serializers.IntegerField(read_only=True)
    phone_number = serializers.CharField(max_length=15)
    role = serializers.CharField(max_length=20)
    created_at = serializers.CharField()
    is_active = serializers.BooleanField()


class WalletSerializer(serializers.Serializer):
    """Serializer for wallet data"""
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField()
    balance = serializers.IntegerField()
    last_updated = serializers.CharField()


class TransactionSerializer(serializers.Serializer):
    """Serializer for transaction data"""
    id = serializers.IntegerField(read_only=True)
    wallet_id = serializers.IntegerField()
    transaction_type = serializers.CharField(max_length=20)
    amount = serializers.IntegerField()
    timestamp = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    exit_id = serializers.IntegerField(allow_null=True, required=False)


class UserPlateSerializer(serializers.Serializer):
    """Serializer for user plate data"""
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField()
    plate = serializers.CharField(max_length=20)
    registered_at = serializers.CharField()
    is_active = serializers.BooleanField()


class LoginRequestSerializer(serializers.Serializer):
    """Serializer for login request"""
    phone_number = serializers.CharField(max_length=15, required=True)


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response"""
    success = serializers.BooleanField()
    token = serializers.CharField()
    user = UserSerializer()
    wallet = WalletSerializer()


class WalletBalanceSerializer(serializers.Serializer):
    """Serializer for wallet balance response"""
    balance = serializers.IntegerField()
    last_updated = serializers.CharField()


class ChargeWalletRequestSerializer(serializers.Serializer):
    """Serializer for wallet charge request"""
    amount = serializers.IntegerField(min_value=1)


class ChargeWalletResponseSerializer(serializers.Serializer):
    """Serializer for wallet charge response"""
    success = serializers.BooleanField()
    new_balance = serializers.IntegerField()
    transaction_id = serializers.IntegerField()


class TransactionListSerializer(serializers.Serializer):
    """Serializer for transaction list response"""
    count = serializers.IntegerField()
    results = TransactionSerializer(many=True)


class AddPlateRequestSerializer(serializers.Serializer):
    """Serializer for add plate request"""
    plate = serializers.CharField(max_length=20, required=True)


class PlateListSerializer(serializers.Serializer):
    """Serializer for plate list response"""
    plates = UserPlateSerializer(many=True)
