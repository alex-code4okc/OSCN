from django.db import models

# Create your models here.
class party(models.Model):
    name = models.CharField(max_length=100,help_text="Enter the plaintiff's name.")
    children = models.BooleanField(blank=True, null=True)
    plaintiff = models.BooleanField(blank=True, null=True)
    defendant = models.BooleanField(blank=True, null=True)
    attorney = models.ForeignKey('attorney',null=True,blank=True,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {'Plaintiff' if self.plaintiff==True else 'Defendant'}"

class judge(models.Model):
    name = models.CharField(max_length=100, help_text="Enter the judge's name.")

    def __str__(self):
        return f"{self.name}"

class attorney(models.Model):
    name = models.CharField(max_length=100, help_text="Enter the attorney's name.")
    bar_number = models.CharField(max_length=20, help_text="Enter the attorney's bar number.", blank = True, null = True)
    address = models.TextField(null=True, blank= True)
    # represented_party = models.ForeignKey(party,null=True,blank=True,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.bar_number})"

class event(models.Model):
    event = models.TextField()
    party = models.CharField(max_length=100, help_text="Enter the parties name.")
    docket = models.CharField(max_length=100,help_text="Enter the judge assigned to the event.")
    reporter = models.CharField(max_length=100, help_text = "Enter the reporter's name.")

    def __str__(self):
        return f"{self.event}"

class issue(models.Model):
    issue_number = models.IntegerField()
    issue_type = models.CharField(max_length=50, help_text="Enter the issue type")
    filed_by = models.ForeignKey(party,on_delete=models.CASCADE)
    filed_date = models.DateField()

    def __str__(self):
        return f"{self.issue_number} - {self.issue_type}\nFiled by: {self.filed_by} on {self.filed_date}"

class DocketEntry(models.Model):
    date = models.DateField()
    code = models.CharField(max_length=50, help_text="Enter the docket code.")
    description = models.TextField()
    count = models.CharField(max_length=10, null=True, blank=True)
    party = models.ForeignKey(party, blank=True, null=True,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    available_at_court_clerk_office = models.BooleanField(blank=True,null=True)
    def __str__(self):
        return f"{self.date} - {self.code}: {self.description}"

class ProtectiveOrder(models.Model):
    po_number = models.CharField(max_length=50, help_text="Enter the protective order PO number.")
    filed_date = models.DateField()
    closed_date = models.DateField(blank=True, null=True)
    judge = models.ForeignKey(judge, on_delete=models.CASCADE, blank=True, null=True)
    plaintiffs = models.ManyToManyField(party, related_name='PO_plaintiffs')
    defendants = models.ManyToManyField(party, related_name='PO_defendants')
    attorneys = models.ManyToManyField(attorney, blank=True)
    events = models.ManyToManyField(event, blank=True)
    issues = models.ManyToManyField(issue, blank=True)
    docket = models.ManyToManyField(DocketEntry, blank=True)
    
    def __str__(self):
        return f"{self.po_number} - Filed: {self.filed_date} - Judge: {self.judge}"



