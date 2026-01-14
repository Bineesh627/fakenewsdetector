from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Submitter
    link_url = models.URLField(null=True, blank=True)
    text = models.TextField()
    prediction = models.CharField(max_length=10)  # 'Real' or 'Fake'
    confidence = models.FloatField()
    approved = models.BooleanField(default=False)  # For retraining eligibility
    created_at = models.DateTimeField(auto_now_add=True)

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
        unique_together = ('prediction', 'user')  # Prevent duplicate votes per user

class Feedback(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='corrections')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Who submitted correction
    corrected_label = models.CharField(max_length=10)  # 'Real' or 'Fake'
    feedback_note = models.TextField(null=True, blank=True)
    approved = models.BooleanField(default=False)  # Admin approval for retraining
    created_at = models.DateTimeField(auto_now_add=True)