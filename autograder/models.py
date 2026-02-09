# autograder/models.py
# autograder/models.py
from django.db import models
from django.utils import timezone

class TeacherQuestion(models.Model):
    """Teacher-created questions with keywords for grading"""
    question_id = models.CharField(max_length=100, unique=True)
    question_text = models.TextField()
    expected_keywords = models.TextField(help_text="Comma-separated keywords")
    model_answer = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Teacher Question"
        verbose_name_plural = "Teacher Questions"
    
    def get_expected_keywords(self):
        """Convert stored keywords string to list of normalized keywords"""
        return [kw.strip().lower() for kw in self.expected_keywords.split(',') if kw.strip()]
    
    def __str__(self):
        return f"{self.question_id}: {self.question_text[:50]}..."


class StudentAnswer(models.Model):
    """Student answer submissions (optional - for storing results)"""
    question = models.ForeignKey(TeacherQuestion, on_delete=models.CASCADE, null=True, blank=True)
    question_id_ref = models.CharField(max_length=100, blank=True)  # Store question_id if question is deleted
    student_name = models.CharField(max_length=200, blank=True)
    extracted_text = models.TextField()
    marks = models.FloatField(default=0.0)
    matched_keywords = models.TextField(blank=True)  # JSON string
    missing_keywords = models.TextField(blank=True)  # JSON string
    uploaded_image = models.ImageField(upload_to='student_answers/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Answer by {self.student_name or 'Anonymous'} - {self.created_at}"