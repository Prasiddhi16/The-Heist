from django.db import models

class Case(models.Model):
    # Anusha, extends this later with status, location, risk_level, or whatever required
    case_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Suspect(models.Model):
    case = models.ForeignKey(Case, related_name="suspects", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50)   
    risk = models.CharField(max_length=20)    

    def __str__(self):
        return self.name


class Evidence(models.Model):
    case = models.ForeignKey(Case, related_name="evidence_items", on_delete=models.CASCADE)
    evidence_id = models.CharField(max_length=20)   
    name = models.CharField(max_length=100)          
    collected_at = models.CharField(max_length=100)
    status = models.CharField(max_length=50)         

    def __str__(self):
        return self.evidence_id