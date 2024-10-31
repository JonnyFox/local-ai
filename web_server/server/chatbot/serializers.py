# chatbot/serializers.py

from rest_framework import serializers


class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    chat_uuid = serializers.CharField()
