from django.db import models


class Case(models.Model):
    case_id = models.IntegerField(primary_key=True, db_column='case_id')
    case_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    loss_value = models.CharField(max_length=100, null=True, blank=True)
    risk_level = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cases'

    def __str__(self):
        return self.title


class Suspect(models.Model):
    suspect_id = models.IntegerField(primary_key=True, db_column='suspect_id')
    case = models.ForeignKey(Case, related_name="suspects", on_delete=models.CASCADE, db_column='case_id')
    name = models.CharField(max_length=100)
    occupation = models.TextField(null=True, blank=True)
    motive = models.TextField(null=True, blank=True)
    alibi = models.TextField(null=True, blank=True)
    alibi_status = models.CharField(max_length=50, null=True, blank=True)
    suspect_status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'suspects'

    def __str__(self):
        return self.name


class Evidence(models.Model):
    evidence_id = models.IntegerField(primary_key=True, db_column='evidence_id')
    case = models.ForeignKey(Case, related_name="evidence_items", on_delete=models.CASCADE, db_column='case_id')
    item_name = models.CharField(max_length=100, db_column='item_name')
    evidence_type = models.CharField(max_length=50, db_column='evidence_type')
    found_at = models.CharField(max_length=100, db_column='found_at')
    details = models.TextField(null=True, blank=True, db_column='details')

    class Meta:
        db_table = 'evidence'

    def __str__(self):
        return self.item_name


class SolutionSuspect(models.Model):
    id = models.BigAutoField(primary_key=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, db_column='case_id')
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, db_column='suspect_id')
    is_guilty = models.BooleanField(default=False)

    class Meta:
        db_table = 'solution_suspects'
        unique_together = ('case', 'suspect')


class SolutionEvidence(models.Model):
    id = models.BigAutoField(primary_key=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, db_column='case_id')
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE, db_column='evidence_id')
    is_key_evidence = models.BooleanField(default=False)

    class Meta:
        db_table = 'solution_evidence'
        unique_together = ('case', 'evidence')


class CaseSubmission(models.Model):
    submission_id = models.BigAutoField(primary_key=True)
    case = models.ForeignKey(Case, related_name='submissions', on_delete=models.CASCADE, db_column='case_id')
    user_id = models.IntegerField(null=True, blank=True, db_column='user_id')  # ← add this line
    narrative = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    is_correct = models.BooleanField(null=True)
    reviewer_notes = models.TextField(null=True, blank=True)
    score = models.IntegerField(default=0)

    class Meta:
        db_table = 'case_submissions'
        ordering = ['-submitted_at']
class SubmissionSuspect(models.Model):
    id = models.BigAutoField(primary_key=True)
    submission = models.ForeignKey(CaseSubmission, on_delete=models.CASCADE, db_column='submission_id')
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, db_column='suspect_id')
    is_accused = models.BooleanField(default=False)

    class Meta:
        db_table = 'submission_suspects'
        unique_together = ('submission', 'suspect')


class SubmissionEvidence(models.Model):
    id = models.BigAutoField(primary_key=True)
    submission = models.ForeignKey(CaseSubmission, on_delete=models.CASCADE, db_column='submission_id')
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE, db_column='evidence_id')
    is_selected = models.BooleanField(default=False)

    class Meta:
        db_table = 'submission_evidence'
        unique_together = ('submission', 'evidence')