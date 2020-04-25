from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1']== request.POST['password2']:
            try:
                user=User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(), "error": "User name already has been taken, please try new one"})
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), "error": "Password did't match"})

@login_required
def currenttodos(request):
    #todos= Todo.objects.all()
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True).order_by('-created')
    return render(request, 'todo/currenttodos.html',{'todos':todos})

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

def home(request):
    todos= Todo.objects.all().order_by('-created')
    return render(request, 'todo/home.html', {'todos':todos})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user=authenticate(request, username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error':'Username and password did not  match!'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html',{'form': TodoForm()})
    else:
        try:
            form=TodoForm(request.POST)
            newtodo =form.save(commit=False)
            newtodo.user= request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(),'error':'Bad data passed in. Please try again'})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk,user=request.user)
    if request.method=="GET":
        form= TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html',{'todo':todo, 'form': form})
    else:
        try:
            form=TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo':todo, 'form': form,'error':'Bad data passed in. Please try again'})

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk,user=request.user)
    if request.method=="POST":
        todo.datecompleted=timezone.now()
        form= TodoForm(instance=todo)
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk,user=request.user)
    if request.method=="POST":
        form= TodoForm(instance=todo)
        todo.delete()
        return redirect('currenttodos')

@login_required
def archived(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/archived.html', {'todos': todos})



@login_required
def justread(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk)
    if request.method=="GET":
        form= TodoForm(instance=todo)
        return render(request, 'todo/justread.html',{'todo':todo, 'form': form})
    else:
        try:
            form=TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/justread.html', {'todo':todo, 'form': form,'error':'Bad data passed in. Please try again'})
