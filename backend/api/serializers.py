from rest_framework import serializers
from .models import Entry, Exit, ActiveCar, Setting


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
