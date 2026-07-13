from django.db import models

class Case(models.Model):
    # Fixed from 'case_i' to 'case_id'
    case_id = models.IntegerField(primary_key=True, db_column='case_id') 
    case_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)

    class Meta:
        db_table = 'cases'

    def __str__(self):
        return self.title


class Suspect(models.Model):
    # Fixed from 'suspect_' to 'suspect_id' and 'case_i' to 'case_id'
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
    # Fixed from 'evidenc' to 'evidence_id' and 'case_i' to 'case_id'
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