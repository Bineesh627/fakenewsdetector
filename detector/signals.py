from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Prediction, Feedback, Vote, ActivityLog

@receiver(post_save, sender=Prediction)
def log_prediction(sender, instance, created, **kwargs):
    if created:
        username = instance.user.username if instance.user else "Anonymous"
        ActivityLog.objects.create(
            actor=instance.user,
            action_type='prediction_created',
            details=f"{username} submitted a new article for analysis"
        )

@receiver(post_save, sender=Feedback)
def log_feedback(sender, instance, created, **kwargs):
    if created:
        username = instance.user.username if instance.user else "Anonymous"
        ActivityLog.objects.create(
            actor=instance.user,
            action_type='feedback_submitted',
            details=f"{username} flagged prediction #{instance.prediction.id} as incorrect"
        )

@receiver(post_save, sender=Vote)
def log_vote(sender, instance, created, **kwargs):
    if created:
        username = instance.user.username if instance.user else "Anonymous"
        action = 'vote_up' if instance.vote_type == 'UP' else 'vote_down'
        verb = 'upvoted' if instance.vote_type == 'UP' else 'downvoted'
        ActivityLog.objects.create(
            actor=instance.user,
            action_type=action,
            details=f"{username} {verb} prediction #{instance.prediction.id}"
        )

@receiver(post_save, sender=User)
def log_user_join(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            actor=instance,
            action_type='user_login', # Using 'user_login' to match existing frontend filters/icons
            details=f"User {instance.username} joined the platform"
        )
