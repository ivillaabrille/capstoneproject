from rest_framework import serializers
from .models import DataSet

class DataSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataSet
        # fields = ('DataSet_Title', 'DataSet_Description')
        fields = '__all__'