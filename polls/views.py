from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.utils import timezone
import json

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))



class QuestionData(View):

    def post(self, request):
        body = json.loads(request.body)

        q = Question(question_text=body["question"], pub_date=timezone.now())
        q.save()
        
        for choice in body["choices"]:
            q.choice_set.create(choice_text=choice["choice"], votes=0)
        
        q.save()
        return JsonResponse({'objects': 0}, status=200)
    
    def get(self, request):
        question_queryset = Question.objects.all()

        # try pylint (vscode) / anaconda (sublime text 3)
        json_objects = [{
            'text': question.question_text,
            'id': question.id
        } for question in reversed(question_queryset)]

        return JsonResponse({'objects': json_objects}, status=200)

class ChoicesData(View):

    def get(self, request, question_id):
        q = Question.objects.get(id=question_id)

        json_objects = [{
            'text': choice.choice_text,
            'votes': choice.votes,
            'id': choice.id
        } for choice in q.choice_set.all()]
        
        return JsonResponse({
            'objects': json_objects,
            'question': q.question_text
            }, status=200)
    
    def post(self, request, question_id):
        body = json.loads(request.body)
        question = get_object_or_404(Question, pk=question_id)
        try:
            selected_choice = question.choice_set.get(pk=body["choice_id"])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            pass
        else:
            selected_choice.votes += 1
            selected_choice.save()
        return JsonResponse({'objects': 0}, status=200)
    
    