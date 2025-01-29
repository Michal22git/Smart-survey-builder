from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    response_count = models.PositiveIntegerField(default=0, editable=False)
    public_id = models.CharField(max_length=16, unique=True, editable=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = self.generate_public_id()
        super().save(*args, **kwargs)

    def generate_public_id(self):
        import secrets
        return secrets.token_urlsafe(8)[:8]


class Question(models.Model):
    QUESTION_TYPES = [
        ('text', 'Odpowiedź tekstowa'),
        ('radio', 'Pojedynczy wybór'),
        ('checkbox', 'Wielokrotny wybór'),
        ('dropdown', 'Lista rozwijana'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='text')
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.survey.title}: {self.text}"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Odpowiedź na {self.survey.title} ({self.created_at})"


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    selected_options = models.ManyToManyField(Option, blank=True)

    def __str__(self):
        return f"Odpowiedź na {self.question.text}"
