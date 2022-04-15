from django.db import models


class Word(models.Model):
    text_input = models.CharField(max_length=100, primary_key=True)  # implies index creation
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.text_input}: {self.count}"
