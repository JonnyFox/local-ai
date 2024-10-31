import io

from langchain_core.caches import RETURN_VAL_TYPE
from django.http import StreamingHttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


from .serializers import SearchSerializer
from .services import ChatbotService


class StreamingHttpResponseExt(StreamingHttpResponse):
    response_buffer = None
    chat_history = None
    question = None

    def __init__(self, *args, **kwargs):
        self.response_buffer = kwargs.pop('response_buffer')
        self.chat_history = kwargs.pop('chat_history')
        self.question = kwargs.pop('question')
        super().__init__(*args, **kwargs)

    def close(self) -> None:
        super().close()
        response_text = self.response_buffer.getvalue()
        self.chat_history.add_user_message(self.question)
        self.chat_history.add_ai_message(response_text)


class SearchAPIView(APIView):

    service = ChatbotService()

    def post(self, request, *args, **kwargs):
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            query_text = serializer.validated_data['query']
            chat_uuid = serializer.validated_data['chat_uuid']

            response_buffer = io.StringIO()
            return StreamingHttpResponseExt(
                self.service.answer_question(query_text, chat_uuid)(response_buffer),
                content_type='text/plain',
                response_buffer=response_buffer,
                chat_history=self.service.get_chat_history(chat_uuid),
                question=query_text,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
