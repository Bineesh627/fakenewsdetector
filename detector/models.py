from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Submitter
    text = models.TextField()
    prediction = models.CharField(max_length=10)  # 'Real' or 'Fake'
    confidence = models.FloatField()
    approved = models.BooleanField(default=False)  # For retraining eligibility
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'predictions'

    def __str__(self):
        return f"{self.prediction} - {self.created_at}"

    @property
    def votes_up(self):
        return self.vote_set.filter(vote_type='UP').count()

    @property
    def votes_down(self):
        return self.vote_set.filter(vote_type='DOWN').count()

class Vote(models.Model):
    VOTE_CHOICES = (
        ('UP', 'Agree'),
        ('DOWN', 'Disagree'),
    )
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votes'
        unique_together = ('prediction', 'user')  # Prevent duplicate votes per user

class Feedback(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='corrections')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Who submitted correction
    corrected_label = models.CharField(max_length=10)  # 'Real' or 'Fake'
    feedback_note = models.TextField(null=True, blank=True)
    approved = models.BooleanField(default=False)  # Admin approval for retraining
    rejected = models.BooleanField(default=False)  # Admin rejection
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'correction_feedbacks'

class DashboardStats(models.Model):
    total_predictions = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    pending_feedback = models.IntegerField(default=0)
    accuracy_rate = models.FloatField(default=100.0)
    real_count = models.IntegerField(default=0)
    fake_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dashboard_metrics'

    def __str__(self):
        return f"Stats updated at {self.updated_at}"

class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('prediction_created', 'Prediction Created'),
        ('feedback_submitted', 'Feedback Submitted'),
        ('vote_up', 'Upvoted'),
        ('vote_down', 'Downvoted'),
        ('user_login', 'User Joined'), # Keeping 'user_login' string for compat with frontend filter
    )
    
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'

    def __str__(self):
        return f"{self.actor} - {self.action_type} - {self.created_at}"