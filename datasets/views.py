from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DataSet
from .serializers import DataSetSerializer
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import DataSetForm, ColumnForm, DataForm, SignUpForm
from django.contrib.auth import login, logout, authenticate
from django.core.urlresolvers import reverse
from django.views import generic
import os
from django.conf import settings
import simplejson
import psycopg2
from django.contrib.auth.views import login
from django.contrib.auth.models import User

#cur = conn.cursor()
# Lists all datasets
# datasets/
class DataSetList(APIView):
    #endpoint
    def get(self, request):
        datasets = DataSet.objects.all().order_by('-DataSet_Posted', '-id')
        serializer = DataSetSerializer(datasets, many=True)
        return Response(serializer.data)

    def post(self):
        pass

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('datasets:signin'))
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'datasets/signup.html', context)

def signin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('datasets:index'))
    else:
        return login(request, template_name='datasets/signin.html')

def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'datasets/signout.html')
    else:
        return HttpResponseRedirect(reverse('datasets:index'))

def IndexView(request):
    return render(request, 'datasets/index.html')

class DataView(generic.ListView):
    template_name = 'datasets/data.html'
    context_object_name = 'all_dataset'

    def get_queryset(self):
        combined_queryset = DataSet.objects.filter(DataSet_Status='Approved') | DataSet.objects.filter(DataSet_Status='Not yet Approved')
        return combined_queryset.order_by('-DataSet_Posted', '-id')

def DataDetailView(request, pk):
    conn = psycopg2.connect("dbname=postgres user=postgres password=capstone")
    try:
        dataset = DataSet.objects.get(pk=pk)
        cur = conn.cursor()
        title = DataSet.objects.get(id=pk)
        #python object
        cur.execute("""SELECT * FROM "{}";""".format(title.id))
        rows = cur.fetchall()
        count = len(rows)
        colnames=[desc[0] for desc in cur.description]
        count2 = len(colnames)
        #csv
        sql = """COPY "%s" TO STDOUT WITH CSV HEADER DELIMITER AS ','"""
        with open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "w") as file:
            cur.copy_expert(sql % title.id, file)
        csvdata = open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "r")
        csv = csvdata.readlines()
        #json
        cur.execute("""SELECT row_to_json("{}") FROM "{}";""".format(title.id, title.id))
        with open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "w") as file2:
            simplejson.dump(cur.fetchall(), file2, indent=2)
        jsondata = open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "r")
        json = jsondata.readlines()
    finally:
        conn.close()

    context = {"dataset": dataset, "rows": rows, "colnames": colnames, "csv": csv, "json": json, "count": count, "count2": count2}
    return render(request, "datasets/datadetail.html", context)

def MyDataView(request):
    if request.user.is_authenticated:
        all_dataset = DataSet.objects.filter(DataSet_Poster=request.user.id)
    else:
        pass

    context = {"all_dataset": all_dataset}
    return render(request, 'datasets/datasets.html', context)

def NewDataView(request):
    if request.method == 'POST':
        form = DataSetForm(data=request.POST)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.DataSet_Poster = request.user
            dataset.save()
            title = DataSet.objects.last()
            conn = psycopg2.connect("dbname=postgres user=postgres password=capstone")
            cur = conn.cursor()
            cur.execute("""CREATE TABLE "%s"(id serial PRIMARY KEY);""" % str(title.id))
            conn.commit();
            conn.close();
            cur.close();
            number = int(request.POST['noofcolumns'])

            return HttpResponseRedirect(reverse('datasets:newdata2', args=[number]))
    else:
        form = DataSetForm()

    context = {'form': form}
    return render(request, 'datasets/newdata.html', context)

def NewData2View(request, number):
    forms = [ColumnForm(data=request.POST or None) for x in range(int(number))]
    if request.method == 'POST':
        index = 0
        lastDataSet = DataSet.objects.last()
        for form in forms:
            if form.is_valid():
                columnname = request.POST.getlist('cname').pop(index)
                columntype = request.POST.getlist('cvalue').pop(index)
                conn = psycopg2.connect("dbname=postgres user=postgres password=capstone")
                cur = conn.cursor()
                cur.execute("""ALTER TABLE "{}" ADD COLUMN "{}" {};""".format(lastDataSet.id, columnname, columntype))
                conn.commit();
                conn.close();
                cur.close();
                index=index+1

        return HttpResponseRedirect(reverse('datasets:datadetail', args=[lastDataSet.id]))

    context = {'forms': forms}
    return render(request, 'datasets/newdata2.html', context)

def AddDataView(request, pk):
    conn = psycopg2.connect("dbname=postgres user=postgres password=capstone")
    cur = conn.cursor()
    title = DataSet.objects.get(id=pk)
    cur.execute("""SELECT * FROM "{}";""".format(title.id))
    colnames = [desc[0] for desc in cur.description]
    count = len(colnames)-1
    cnames = ''
    colname = [desc[0] for desc in cur.description]
    colname.remove('id')
    for x in colname:
        cnames = cnames + '"' + x + '", '
    cnames = cnames[:-2]

    forms = [DataForm(data=request.POST or None) for x in range(int(count))]
    if request.method == 'POST':
        for form in forms:
            if form.is_valid():
                values = ''
                for x in request.POST.getlist('dvalue'):
                    values = values + "'" + x + "', "
                values = values[:-2]
        cur = conn.cursor()
        cur.execute("""INSERT INTO "{}"({}) VALUES({});""".format(title.id, cnames, values))
        conn.commit();
        conn.close();
        cur.close();

        return HttpResponseRedirect(reverse('datasets:datadetail', args=[title.id]))

    context = {'forms': forms, "colnames": colname, "count": count}
    return render(request, 'datasets/adddata.html', context)

def AboutView(request):
    return render(request, 'datasets/about.html')


# class DataDetailView(generic.DetailView):
#     model = DataSet
#     template_name = 'datasets/datadetail.html'
#     query_pk_and_slug = True
#
#     def get_context_data(self, **kwargs):
#         conn = psycopg2.connect("dbname=postgres user=postgres password=capstone")
#         cur = conn.cursor()
#         title = DataSet.objects.get(pk=self.kwargs['pk'])
#         #python object
#         cur.execute("""SELECT * FROM {}""".format(title.DataSet_Title))
#         rows = cur.fetchall()
#         #csv
#         sql = """COPY %s TO STDOUT WITH CSV HEADER DELIMITER AS ','"""
#         with open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "w") as file:
#             cur.copy_expert(sql % title.DataSet_Title, file)
#         csvdata = open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "r")
#         csv = csvdata.readlines()
#         #json
#         cur.execute("""SELECT row_to_json({}) FROM {};""".format(title.DataSet_Title, title.DataSet_Title))
#         with open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "w") as file2:
#             simplejson.dump(cur.fetchall(), file2, indent=2)
#         jsondata = open(os.path.join(settings.MEDIA_ROOT, 'data.json'), "r")
#         json = jsondata.readlines()
#
#         conn.close();
#         cur.close();
#         context = {"rows": rows, "csv": csv, "json": json}
#         return context

# class GetCsvView(generic.DetailView):
#     model = DataSet
#     template_name = 'datasets/getcsv.html'
#     query_pk_and_slug = True
#
#     def get_context_data(self, **kwargs):
#         conn = psycopg2.connect("dbname=postgres user=postgres password=capstone")
#         cur = conn.cursor()
#         title = DataSet.objects.get(pk=self.kwargs['pk'])
#         sql = """COPY %s TO STDOUT WITH CSV HEADER DELIMITER AS ','"""
#         with open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "w") as file:
#             cur.copy_expert(sql % title.DataSet_Title, file)
#         conn.close();
#         cur.close();
#         fh = open(os.path.join(settings.MEDIA_ROOT, 'data.csv'), "r")
#         rows = fh.readlines()
#         context = {"rows": rows}
#
#         return context

# class GetJsonView(generic.DetailView):
#     model = DataSet
#     template_name = 'datasets/getjson.html'
#     query_pk_and_slug = True
#
#     def get_context_data(self, **kwargs):
#         conn = psycopg2.connect("dbname=postgres user=postgres password=capstone")
#         cur = conn.cursor()
#         title = DataSet.objects.get(pk=self.kwargs['pk'])
#         cur.execute("""SELECT row_to_json({}) FROM {};""".format(title.DataSet_Title, title.DataSet_Title))
#         rows = cur.fetchall()
#         conn.close();
#         cur.close();
#         context = {"rows": rows}
#
#         return context

# class MyDataView(generic.ListView):
#     template_name = 'datasets/datasets.html'
#     context_object_name = 'all_dataset'
#
#     def get_queryset(self):
#         combined_queryset = DataSet.objects.filter(DataSet_Poster='1')
#         return combined_queryset.order_by('-DataSet_Posted', '-id')