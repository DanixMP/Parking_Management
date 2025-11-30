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


class User(models.Model):
    """Model for user accounts"""
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('user', 'User'),
            ('admin', 'Admin'),
            ('superuser', 'SuperUser')
        ],
        default='user'
    )
    created_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return f"{self.phone_number} ({self.role})"


class Wallet(models.Model):
    """Model for user wallets"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')
    balance = models.IntegerField(default=0)
    last_updated = models.DateTimeField()

    class Meta:
        db_table = 'wallets'
        managed = False

    def __str__(self):
        return f"Wallet for {self.user.phone_number}: {self.balance} Rials"


class Transaction(models.Model):
    """Model for wallet transactions"""
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, db_column='wallet_id')
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('charge', 'Charge'),
            ('payment', 'Payment'),
            ('refund', 'Refund')
        ]
    )
    amount = models.IntegerField()
    timestamp = models.DateTimeField()
    description = models.TextField(blank=True)
    exit_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'transactions'
        managed = False
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} Rials at {self.timestamp}"


class UserPlate(models.Model):
    """Model for user-registered license plates"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    plate = models.CharField(max_length=20)
    registered_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_plates'
        managed = False
        unique_together = ('user', 'plate')

    def __str__(self):
        return f"{self.plate} - {self.user.phone_number}"


class AuthToken(models.Model):
    """Model for authentication tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'auth_tokens'
        managed = False

    def __str__(self):
        return f"Token for {self.user.phone_number}"
