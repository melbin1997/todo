from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from tasks.models import Task

class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted = False, user=self.request.user)


class UserLoginView(LoginView):
    template_name = "user_login.html"

class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"

def session_storage_view(request):
    total_views = request.session.get('total_views', 0)
    request.session['total_views'] = total_views + 1
    return HttpResponse(f'Total views is {total_views} and the user id is {request.user}')

class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"

    def form_valid(self, form):
        success_url = self.get_success_url()
        Task.objects.filter(id=self.object.id).update(deleted = True)
        return HttpResponseRedirect(success_url)

class GenericTaskDetailView(AuthorizedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"



class TaskCreateForm(ModelForm):
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise ValidationError("Data too small")
        return title.upper()

    class Meta:
        model = Task
        fields = ("title", "description", "completed", "priority")

class GenericTaskUpdateView(AuthorizedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        if Task.objects.filter(priority=self.object.priority, deleted = False, completed = False, user = self.request.user).exists():
            Task.objects.filter(priority__gte=self.object.priority, deleted = False, completed = False, user = self.request.user).update(priority = F('priority')+1)

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class GenericTaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        if Task.objects.filter(priority=self.object.priority, deleted = False, completed = False, user = self.request.user).exists():
            Task.objects.filter(priority__gte=self.object.priority, deleted = False, completed = False, user = self.request.user).update(priority = F('priority')+1)

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskView(LoginRequiredMixin ,ListView):
    queryset = Task.objects.filter(deleted = False, completed = False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(deleted = False, completed = False, user=self.request.user).order_by('priority')
        if search_term:
            tasks = tasks.filter(title__icontains = search_term)
        return tasks

class CreateTaskView(LoginRequiredMixin, View):
    def get(self,request):
        return render(request, "task_create.html")

    def post(self, request):
        task_value = request.POST.get('task')
        Task(title = task_value).save()
        return HttpResponseRedirect("/tasks")

class TaskView(View):
    def get(self, request):
        search_term = request.GET.get("search")
        tasks = Task.objects.filter(deleted = False, completed = False)
        if search_term:
            tasks = tasks.filter(title__icontains = search_term)
        return render(request, "tasks.html", {"tasks":tasks})

def tasks_view(request):
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted = False, completed = False)
    if search_term:
        tasks = tasks.filter(title__icontains = search_term)
    return render(request, "tasks.html", {"tasks":tasks})

def add_task_view(request):
    task_value = request.GET.get('task')
    Task(title = task_value).save()
    return HttpResponseRedirect("/tasks")

def delete_task_view(request, index):
    task_obj = Task.objects.filter(id=index, user = request.user)
    task_obj.update(deleted = True)
    return HttpResponseRedirect("/tasks")

def complete_task_view(request,index):
    Task.objects.filter(id=index, user = request.user).update(completed = True)
    return HttpResponseRedirect("/tasks")

def complete_list_view(request):
    completed_tasks = Task.objects.filter(completed = True, user=request.user)
    return render(request, "completed_tasks.html", {"tasks":completed_tasks})

def all_tasks_view(request):
    tasks = Task.objects.filter(deleted = False, completed = False, user = request.user)
    completed_tasks = Task.objects.filter(completed = True, user = request.user)

    return render(request, "all_tasks.html", {"tasks":tasks, "completed_tasks":completed_tasks})


class GenericAllTaskView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'all_tasks'   
    template_name = 'all_tasks.html'
    paginate_by = 5

    def get_queryset(self):
        all_tasks = Task.objects.filter(deleted = False, user = self.request.user).order_by('completed','priority')
        return all_tasks

    def get_context_data(self, **kwargs):
        context = super(GenericAllTaskView, self).get_context_data(**kwargs)
        context['tasks'] = Task.objects.filter(deleted = False, completed = False, user = self.request.user).order_by('priority')
        context['completed_tasks'] = Task.objects.filter(completed = True, user = self.request.user).order_by('priority')
        all_tasks = Task.objects.filter(deleted = False, user = self.request.user).order_by('completed','priority')
        context['completed_count'] = all_tasks.filter(completed=True).count()
        context['all_count'] = all_tasks.count()
        return context


class GenericTaskCompleteListView(LoginRequiredMixin ,ListView):
    template_name = "completed_tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        completed_tasks = Task.objects.filter(completed = True, deleted = False, user=self.request.user).order_by('priority')
        return completed_tasks

# Alternative class of GenericTaskCompleteUpdateView
class GenericTaskCompleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    success_url = "/tasks"

    def form_valid(self, form):
        success_url = self.get_success_url()
        Task.objects.filter(id=self.object.id).update(completed = True)
        return HttpResponseRedirect(success_url)


class GenericTaskCompleteUpdateView(AuthorizedTaskManager, UpdateView):
    model = Task
    fields = ("completed",)
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.completed = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())