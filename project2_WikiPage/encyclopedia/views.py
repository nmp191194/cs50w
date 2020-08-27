import markdown2
import numpy as np

from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util

class NewEntryForm(forms.Form):
    entry_title = forms.CharField(label='',
                                 initial='A title for your entry',
                                 validators=[util.check_duplicate_entry])
    entry_content = forms.CharField(label='',
                                    widget=forms.Textarea(attrs={'style': 'height: 30em;'}))

class EditEntryForm(forms.Form):
    entry_content = forms.CharField(label='',
                                    widget=forms.Textarea(attrs={'style': 'height: 30em;'}))


def index(request):
    search_query = request.GET.get('q', '')
    if search_query:
        content = util.get_entry(search_query)
        if (content):
            return HttpResponseRedirect(reverse("encyclopedia:entry_page", args=(search_query,)))
        else:
            results = util.search_entries(search_query)
            if (len(results) == 0):
                return render(request, "encyclopedia/index.html", {
                    "heading": "No ages found for \"" + search_query + "\".",
                    "entries": results
                })
            else:
                return render(request, "encyclopedia/index.html", {
                    "heading": "Pages found for \"" + search_query + "\":",
                    "entries": results
                })
    else:
        return render(request, "encyclopedia/index.html", {
            "heading" : "All Pages",
            "entries": util.list_entries()
        })

def entry_page(request, title):
    content = util.get_entry(title)
    if (content):
        return render(request, "encyclopedia/entry_page.html", {
            'title' : title,
            'content' : markdown2.markdown(content)
        })
    else:
        return render(request, "encyclopedia/error_page.html")

def add(request):
    if request.method == 'POST':
        form = NewEntryForm(request.POST)
        if form.is_valid() :
            title = form.cleaned_data['entry_title']
            content = form.cleaned_data['entry_content']
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:entry_page", args=(title,)))
        else:
            return render(request, 'encyclopedia/add_entry.html', {
                'form' : form
            })

    return render(request, 'encyclopedia/add_entry.html', {
        'form' : NewEntryForm()
    })

def edit(request, title):
    if request.method == 'POST':
        form = EditEntryForm(request.POST)
        if form.is_valid() :
            content = form.cleaned_data['entry_content']
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:entry_page", args=(title,)))
        else:
            return render(request, 'encyclopedia/edit_entry.html', {
                'form' : form
            })
    content = util.get_entry(title)
    if (content):
        print(title)
        form = EditEntryForm({'entry_title': title, 'entry_content': content})
        return render(request, 'encyclopedia/edit_entry.html', {
            'form': form,
            'title': title
        })
    else:
        return render(request, "encyclopedia/error_page.html")

def random(request):
    entries = util.list_entries()
    random_entry = entries[np.random.randint(0,len(entries))]
    if (random_entry):
        return HttpResponseRedirect(reverse("encyclopedia:entry_page", args=(random_entry,)))
    else:
        return render(request, "encyclopedia/error_page.html")