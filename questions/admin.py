from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Question, Subject, Chapter, Topic, Category
from .forms import BulkUploadForm
import csv
import io
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Question, Subject, Chapter, Topic, Category
from .forms import BulkUploadForm
import csv
import io

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'subject', 'chapter', 'topic', 'difficulty', 'question_type', 'created_at')
    list_filter = ('difficulty', 'question_type', 'subject')
    search_fields = ('text', 'subject__name', 'chapter__name', 'topic__name')
    change_list_template = "admin/questions/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload), name='bulk_upload_questions'),
            path('download-template/', self.admin_site.admin_view(self.download_csv_template), name='download_csv_template'),
        ]
        return custom_urls + urls

    def bulk_upload(self, request):
        if request.method == "POST":
            form = BulkUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES.get('csv_file')
                if not csv_file:
                    messages.error(request, "No file was uploaded. Please upload a CSV file.")
                    return HttpResponseRedirect(request.path_info)

                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'Please upload a valid CSV file.')
                    return HttpResponseRedirect(request.path_info)

                try:
                    data_set = csv_file.read().decode('UTF-8')
                    io_string = io.StringIO(data_set)
                    reader = csv.DictReader(io_string)

                    for row in reader:
                        # Get or create the category
                        category_name = row.get('category')
                        category = None
                        if category_name:
                            category, _ = Category.objects.get_or_create(name=category_name)

                        Question.objects.create(
                            text=row.get('text'),
                            category=category,
                            subject_id=row.get('subject_id'),
                            chapter_id=row.get('chapter_id'),
                            topic_id=row.get('topic_id'),
                            difficulty=row.get('difficulty'),
                            question_type=row.get('question_type'),
                            option1=row.get('option1'),
                            option2=row.get('option2'),
                            option3=row.get('option3'),
                            option4=row.get('option4'),
                            correct_answer=row.get('correct_answer'),
                        )
                    messages.success(request, 'Bulk upload completed successfully!')
                    return redirect('admin:questions_question_changelist')
                except Exception as e:
                    messages.error(request, f'Error processing file: {e}')
                    return HttpResponseRedirect(request.path_info)
            else:
                messages.error(request, 'Invalid form submission.')
        else:
            form = BulkUploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/questions/bulk_upload.html", context)


    def download_csv_template(self, request):
    # Define CSV template fields
        template_fields = [
            "text", "category", "subject_id", "chapter_id", "topic_id", "difficulty",
            "question_type", "option1", "option2", "option3", "option4", "correct_answer"
        ]

        # Create response with CSV content
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="question_template.csv"'

        writer = csv.writer(response)
        writer.writerow(template_fields)  # Header row with field names
        writer.writerow([
            "Sample question text", "Sample Category", 1, 1, 1, "easy",
            "MCQ", "Option 1", "Option 2", "Option 3", "Option 4", "option1"
        ])  # Sample data row

        return response


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')
    list_filter = ('subject',)
    search_fields = ('name',)

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'chapter')
    list_filter = ('chapter',)
    search_fields = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register models
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
