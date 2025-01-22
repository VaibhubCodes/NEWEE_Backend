from django.db import models
from django.conf import settings
from quizzes.models import Quiz, SectionQuestion
from django.utils.timezone import now
from datetime import timedelta

import logging
logger = logging.getLogger(__name__)
class Participant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_participations"
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="participants")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)
    total_marks = models.FloatField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    result_status = models.BooleanField(default=False, help_text="Result visibility control by admin.")

    def calculate_score_and_accuracy(self):
        logger.info(f"Calculating score for participant: {self.id}")
        answers = self.answers.select_related('section_question').all()
        correct_answers = sum(1 for answer in answers if answer.is_correct)
        score = sum(answer.marks_obtained for answer in answers)
        Participant.objects.filter(id=self.id).update(
            correct_answers=correct_answers,
            score=score
        )
        logger.info(f"Score calculated for participant: {self.id}, score: {score}")

    def handle_unanswered_questions(self):
        """
        Handle unanswered questions by marking them as incorrect.
        """
        answered_question_ids = self.answers.values_list('section_question_id', flat=True)
        unanswered_questions = SectionQuestion.objects.filter(
            section__quiz=self.quiz
        ).exclude(id__in=answered_question_ids)

        Answer.objects.bulk_create([
            Answer(
                participant=self,
                section_question=section_question,
                selected_option=None,
                is_correct=False,
                marks_obtained=0
            ) for section_question in unanswered_questions
        ])

    def save(self, *args, **kwargs):
        """
        Custom save method to control update_fields to avoid unnecessary updates.
        """
        if 'update_fields' in kwargs and not kwargs['update_fields']:
            kwargs['update_fields'] = ['rank', 'completed_at', 'score', 'correct_answers']
        super().save(*args, **kwargs)

    def get_time_taken(self):
        """
        Calculate the time taken to complete the quiz.
        """
        if self.completed_at:
            time_taken = self.completed_at - self.started_at
            return time_taken
        return timedelta()

    def submit_quiz(self):
        """
        Submit the quiz manually by the participant.
        """
        self.handle_unanswered_questions()  # Mark unanswered questions
        self.completed_at = now()
        self.calculate_score_and_accuracy()
        self.save()

    def auto_submit_quiz(self):
        """
        Automatically submit the quiz when time expires.
        """
        if not self.completed_at:
            self.handle_unanswered_questions()  # Mark unanswered questions
            self.completed_at = now()
            self.calculate_score_and_accuracy()
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"


class Answer(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="answers")
    section_question = models.ForeignKey(SectionQuestion, on_delete=models.CASCADE, related_name="answers")
    selected_option = models.CharField(max_length=50, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    marks_obtained = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:  # Avoid re-evaluating on updates
            # Calculate correctness and marks only for new answers
            self.is_correct = (
                self.selected_option == self.section_question.question.correct_answer
            )
            self.marks_obtained = self.section_question.marks if self.is_correct else 0

        super().save(*args, **kwargs)



    def __str__(self):
        return f"Answer by {self.participant.user.username} for {self.section_question.question.text[:50]}"


class Leaderboard(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="leaderboards")
    generated_at = models.DateTimeField(auto_now_add=True)

    def calculate_leaderboard(self):
        """
        Calculate ranks based on maximum correct answers and fastest completion.
        """
        participants = Participant.objects.filter(quiz=self.quiz).order_by(
            "-correct_answers", "completed_at"
        )
        ranks = []
        for rank, participant in enumerate(participants, start=1):
            ranks.append((participant.id, rank))

        # Bulk update ranks
        Participant.objects.filter(id__in=[r[0] for r in ranks]).update(
            rank=models.Case(
                *[
                    models.When(pk=participant_id, then=models.Value(rank))
                    for participant_id, rank in ranks
                ],
                default=models.Value(None),
                output_field=models.IntegerField(),
            )
        )



    def auto_update_ranks(self):
        """
        Automatically update ranks when a participant submits the quiz or at quiz end time.
        """
        self.calculate_leaderboard()

    def __str__(self):
        return f"Leaderboard for {self.quiz.title}"