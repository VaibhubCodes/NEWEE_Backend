from django import forms

class BulkUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV file")
