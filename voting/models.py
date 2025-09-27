from django.db import models
from django.conf import settings
from django.utils import timezone

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)  # DB column that existed — keep it
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='created_elections')

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        On save, set the is_active flag based on start/end times.
        Note: this keeps DB column in sync when creating/updating an election.
        (If you want dynamic real-time active-state without re-saving,
        change downstream logic to compute from start/end instead.)
        """
        now = timezone.now()
        # set is_active when saving (this solves the NOT NULL constraint and admin create issue)
        try:
            self.is_active = (self.start_time <= now < self.end_time)
        except Exception:
            # if start_time/end_time not set yet (e.g. during migration), keep default
            pass
        super().save(*args, **kwargs)

    def has_ended(self):
        return timezone.now() >= self.end_time


class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.election.title})"


class Vote(models.Model):
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'election'], name='unique_vote_per_user_per_election')
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.voter} -> {self.candidate} @ {self.election}"
