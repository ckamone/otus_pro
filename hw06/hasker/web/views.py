from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.core.paginator import Paginator
from users.models import CustomUser
from web.tasks import send_email
from web.models import (
    Question, Tag, Reply
)
from web.mixins import (
    OnlyStaffMixin,
    OnlySuperMixin,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from web.forms import QuestionCreateForm
from django.http import JsonResponse

# Create your views here.
def main_page(request):
    return render(request, 'web/index.html')


class QuestionListView(ListView):
    model = Question
    paginate_by = 3
    ordering = ('-created_at',)


# class QuestionCreateView(LoginRequiredMixin, CreateView):
#     model = Question
#     fields = ['title', 'text', 'tags']
#     success_url = reverse_lazy('ask_list')

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionCreateForm
    success_url = reverse_lazy('ask_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        context = {}
        context['message'] = ''
        form = QuestionCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            #cheq tags
            tags = data.get('tags_str', None)
            if len(tags.split(',')) > 3:
                context['message'] = 'error: max. tag number is 3'
                return render(request, "web/result.html", context=context)

            # add question model
            title = data.get('title', None)
            text = data.get('text', None)
            user = User.objects.filter(username=request.user)[0]
            que_obj = Question.objects.create(
                title=title,text=text,author=user)
            que_obj.save()

            # add tags
            if tags != '':
                tags = tags.replace(' ','_').split(',_')
                for tag in tags:
                    tag_obj = Tag.objects.create(tag_name=tag)
                    tag_obj.save()
                    # que_obj.tags.add(tag_obj)
                    tag_obj.question.add(que_obj.pk)
                    # que_obj.save()
                context['message'] = 'success'
            return render(request, "web/result.html", context=context)


class QuestionDetailView(LoginRequiredMixin, DetailView):
    model = Question


class TagListView(ListView):
    model = Tag


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    fields = '__all__'
    success_url = reverse_lazy('tag_list')

class FormattedQuestion:
    def __init__(self,question,replies,tags,votes):
        self.question = question
        self.replies = replies
        self.tags = tags
        self.votes = votes

def get_voters(voters):
    return len(voters.split(',')) -1 if voters!='' else 0


def base_questions(request, questions):
    temp = []
    for question in questions:
        temp.append({
            'title': question.title,
            'question_pk': question.pk,
            'author_pk': question.author.pk,
            'tags': Tag.objects.filter(question=question),
            'replies': len(Reply.objects.filter(question=question)),
            'date': question.created_at,
            'author': question.author,
            'votes': get_voters(question.voters_up) - get_voters(question.voters_down),
            'voters_up': question.voters_up,
            'voters_down': question.voters_down,
            # 'voters': len(question.voters_up.split(',')) if question.voters_up!='[]' else 0,
        })
    paginator = Paginator(temp, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'web/new_questions.html', context=context)

def new_questions(request):
    questions = Question.objects.all().order_by('-created_at')
    return base_questions(request, questions)


def hot_questions(request):
    questions = Question.objects.all().order_by('-votes')
    return base_questions(request, questions)

    
def search_questions(request):
    if request.method =="POST":
        searched = request.POST['searched']
        if 'tag:' in searched:
            tags = Tag.objects.filter(tag_name=searched.replace('tag:','').lstrip()).values('question')
            questions = Question.objects.filter(id__in=tags)
        else:
            questions = Question.objects.filter(title__icontains=searched)
            questions_by_text = Question.objects.filter(text__icontains=searched)
            questions |= questions_by_text.order_by('-created_at')
        return base_questions(request, questions)
    else:
        return new_questions(request)

def voteup(user, vote):
    obj_class = Reply if 'r_' in vote else Question
    
    temp_obj = obj_class.objects.filter(pk=vote.split('_')[-1])[0]
    user = User.objects.filter(username=user)[0]
    if user.username not in temp_obj.voters_up:
        temp_obj.voters_up += user.username +','
        temp_obj.votes += 1
        if user.username in temp_obj.voters_down:
            temp_obj.voters_down = temp_obj.voters_down.replace(f'{user.username},','')
            temp_obj.votes += 1
        temp_obj.save()
        return "DEBUG: vote + added" + f'({vote, user})'
    return "DEBUG: already voted" + f'({vote, user})'


def votedown(user, vote):
    obj_class = Reply if 'r_' in vote else Question
    
    temp_obj = obj_class.objects.filter(pk=vote.split('_')[-1])[0]
    user = User.objects.filter(username=user)[0]
    if user.username not in temp_obj.voters_down:
        temp_obj.voters_down += user.username +','
        temp_obj.votes -= 1
        if user.username in temp_obj.voters_up:
            temp_obj.voters_up = temp_obj.voters_up.replace(f'{user.username},','')
            temp_obj.votes -= 1
        temp_obj.save()
        return "DEBUG: vote - added" + f'({vote, user})'
    return "DEBUG: already voted" + f'({vote, user})'


# страница с вопросом и ответами
def question_detailed(request, **kwargs):
    if request.method =="POST":
        if not request.user.is_authenticated:
            return render(request, 'web/result.html', {"message": "login to make vote"})
        if 'voteup' in request.POST:
            result = voteup(request.user, request.POST.get('voteup'))
            return render(request, 'web/result.html', {"message": result})
            
        elif 'votedown' in request.POST:
            result = votedown(request.user, request.POST.get('votedown'))
            return render(request, 'web/result.html', {"message": result})
        else:
            question = Question.objects.filter(pk=kwargs.get('pk'))[0]
            reply = Reply.objects.create(
                text=request.POST['replied'],
                author=User.objects.filter(pk=request.user.pk)[0],
                question=question,
            )
            reply.save()
            ### add email send
            # test_func(request.path, request.method)
            send_email(question)
        return render(request, 'web/result.html', {"message": "success"})
    else:
        question = Question.objects.filter(pk=kwargs.get('pk'))[0]
        # print(80*'*')
        # print(question.author.pk)
        question_user = CustomUser.objects.get(user=question.author.pk)
        # print(question_user.avatar)
        l = {
            "question_obj":question,
            "avatar":question_user.avatar,
            "votes": question.votes,
        }
        tags = Tag.objects.filter(question=question.pk)
        replies = Reply.objects.filter(question=question.pk).order_by('-votes','-created_at')
        temp = []
        for reply in replies:
            reply_user = CustomUser.objects.get(user=reply.author.pk)
            temp.append({
                "reply_obj": reply,
                "avatar": reply_user.avatar,
                "votes": reply.votes,
                "voters_up":reply.voters_up,
                "voters_down":reply.voters_down,
                "correct": reply.is_correct,

            })
        paginator = Paginator(temp, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj, 'question':l, 'tags': tags}
        return render(request, 'web/question_detail2.html', context=context)


def mark_reply(request, **kwargs):
    reply_obj = Reply.objects.get(pk=kwargs.get('pk'))
    if reply_obj.question.author == request.user:
        reply_obj.is_correct = True
        reply_obj.save()
        context = {'message': 'ok'}
    else:
        context = {'message': "error: you can't do that"}
    return render(request, 'web/result.html', context=context)

def get_trending(request):
    questions = Question.objects.all().order_by('-votes','-created_at')
    context = {}
    for i, question in enumerate(questions):
        context[i] = {
            "title": question.title,
            "rating": question.votes,
        }

    return JsonResponse(context)