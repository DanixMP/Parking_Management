from django.db import models


class Entry(models.Model):
    """Model for vehicle entry records"""
    plate = models.CharField(max_length=20)
    image_in = models.CharField(max_length=255)
    timestamp_in = models.DateTimeField()

    class Meta:
        db_table = 'entries'
        managed = False

    def __str__(self):
        return f"{self.plate} - {self.timestamp_in}"


class Exit(models.Model):
    """Model for vehicle exit records"""
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, db_column='entry_id')
    plate = models.CharField(max_length=20)
    image_out = models.CharField(max_length=255)
    timestamp_out = models.DateTimeField()
    duration_minutes = models.IntegerField()
    cost = models.IntegerField()

    class Meta:
        db_table = 'exits'
        managed = False

    def __str__(self):
        return f"{self.plate} - {self.timestamp_out}"


class ActiveCar(models.Model):
    """Model for currently parked vehicles"""
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE, primary_key=True, db_column='entry_id')
    plate = models.CharField(max_length=20)
    timestamp_in = models.DateTimeField()

    class Meta:
        db_table = 'active_cars'
        managed = False

    def __str__(self):
        return f"{self.plate} - Active"


class Setting(models.Model):
    """Model for parking settings"""
    key = models.CharField(max_length=50, primary_key=True)
    value = models.TextField()

    class Meta:
        db_table = 'settings'
        managed = False

    def __str__(self):
        return f"{self.key}: {self.value}"
