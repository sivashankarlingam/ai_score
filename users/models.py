from django.db import models

# Create your models here.
class UserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=100)
    email = models.CharField(unique=True, max_length=100)
    locality = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'UserRegistrations'


class ScoreHistory(models.Model):
    loginid = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    essay_snippet = models.TextField()
    score = models.CharField(max_length=20)
    scored_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loginid} - {self.score} ({self.scored_at})"

    class Meta:
        db_table = 'ScoreHistory'
        ordering = ['-scored_at']

