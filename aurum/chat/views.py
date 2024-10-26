import threading
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from core.models import *
from .models import *
from huggingface_hub import InferenceClient
from .llm import parse_markdown
import requests
import json

BASE_URL = "http://127.0.0.1:8000"  # Replace with your actual API URL

def query_get_ipo(term):
    if term == 'short':
        term = 'short term'
    elif term == 'long':
        term = "long term"
    else:
        term = "neutral"
    response = requests.post(f"{BASE_URL}/get_ipo", json={"term": term})
    print(term)
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def query_get_mf(term, budget):
    if term == 'short':
        term = "Short-Term Schemes"
        budget = "Low"
    elif term == 'long':
        term = "Long-Term Schemes"
        budget = "High"
    else:
        term = "Long-Term Schemes"
        budget = "Medium"
    print(term, budget)
    response = requests.post(f"{BASE_URL}/get_mf", json={"term": term, "budget": budget})
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

class create_chat(View):
    def get(self, request):
        return render(request, 'chat/start_chat.html')
    def post(self, request):
        title = request.POST.get('content')
        user = request.user

        chat = Chat.objects.create(
            title = title,
            user = user
        )
        prompt = "You are Aurum, a conversational chatbot designed to help users find investment opportunities based on their requirements. You must suggest IPOs and Mutual Funds to the user based on the context provided to you. Kindly refrain from answering if the question is not related to personal finance. You must not mention context to the user or talk about stocks outside of the context. If a user sends a non comprehensible message, kindly ask them to repeat. If the context is empty, apologise to the user and tell him to try with different options."

        Message.objects.create(
            chat = chat,
            sender = "system",
            content = prompt
        )

        Message.objects.create(
            chat = chat,
            sender = "assistant",
            content = "Hi! I am Aurum. Please tell me if you are looking for long term or short term investment opportunities and your budget.",
            content_html = "Hi! I am Aurum. Please tell me if you are looking for long term or short term investment opportunities and your budget."
        )

        Message.objects.create(
            chat=chat,
            sender = 'user',
            content = title
        )

        

        if 'long' in title.lower():
            term = 'long'
            budget = 'high'
        elif 'short' in title.lower():
            term = 'short'
            budget = 'low'
        else:
            term = 'neutral'
            budget = 'medium'

        ipo_details = query_get_ipo(term)
        mf_details = query_get_mf(term, budget)

        context_data = {
            "ipo_details": ipo_details,
            "mf_details": mf_details
        }

        chat.context = json.dumps(context_data)  
        chat.save()

        Message.objects.create(
            chat=chat,
            sender = 'system',
            content = chat.context
        )

        Message.objects.create(
            chat=chat,
            sender = 'assistant',
            content = "Thinking..."
        )

        response = HttpResponse() 
        response['HX-Redirect'] = f'/chat/{chat.id}'
        return response 

class chat(View):
    def get(self, request, chatid):
        context = {}
        chat = get_object_or_404(Chat, id = chatid)
        if chat.user != request.user:
            return HttpResponse('Not Found', status=404)
        context['chat'] = chat

        message = chat.messages.last()
        if message and message.content == "Thinking...":
            messages = chat.messages.all()
            thread = threading.Thread(target=self.llm_response, args=(message.id,messages))
            thread.start()
            return render(request, 'chat/chat.html', context)

        return render(request, 'chat/chat.html', context)
    
    def post(self, request, chatid):
        chat = Chat.objects.get(id = chatid)
        content = request.POST.get('content')
        response = chat.messages.last()
        if response and response.content == "Thinking...":
            agent_message_html = render_to_string('chat/partials/error.html', {'error_message': "Please wait till previous request is processed", 'note':'Please refresh the page if it is taking too long'})
            return HttpResponse(agent_message_html)
        if content and content.strip():
            if len(content) > 500:
                agent_message_html = render_to_string(
                    'chat/partials/error.html',
                    {
                        'error_message': "Message exceeds character limit",
                        'note':'Maximum prompt length is 500 characters'
                    }
                )
                return HttpResponse(agent_message_html)

            user_message = Message.objects.create(sender="user", content=content, chat=chat)
            user_message_html = render_to_string('chat/partials/message.html', {'message': user_message})
            agent_message = Message.objects.create(
                sender="assistant", 
                content="Thinking...", 
                chat=chat
            )
            agent_message_html = render_to_string('chat/partials/hot_response.html', {'message': agent_message})
            messages = user_message_html + agent_message_html
            message_history = chat.messages.all()
            thread = threading.Thread(target=self.llm_response, args=(agent_message.id,message_history))
            thread.start()
            return HttpResponse(messages)
        else:
            return HttpResponse('Invalid request', status=400)

    def llm_response(self, messageid, messages):
        message_history = []
        for m in messages:
            message = {}
            message["role"] = m.sender
            message["content"] = m.content
            message_history.append(message)
        print(message_history)
        try:
            client = InferenceClient(
                "microsoft/Phi-3.5-mini-instruct",
                token="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",
            )
            response = client.chat_completion(
                    messages=message_history,
                    max_tokens=500,
                    stream=False,
                )
            agent_message = Message.objects.get(id=messageid)
            response_message = parse_markdown(response.choices[0].message.content)
            agent_message.content = response.choices[0].message.content
            agent_message.content_html = response_message
            agent_message.save()
        except:
            agent_message = Message.objects.get(id=messageid)
            agent_message.sender = "system"
            agent_message.content = "Something went wrong while generating response"
            agent_message.save()

def get_response(request, chat_id):
    user_profile = request.user
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.user != user_profile:
        return HttpResponse('Not Found', status=404)
    response = chat.messages.last()
    if response.content == "Thinking...":
        response_html = render_to_string('chat/partials/hot_response.html',  {'message': response})
    else:
        context = {}
        context["message"] = response
        response_html = render_to_string('chat/partials/response.html', context)
    return HttpResponse(response_html)

def index(request):
    context = {}
    user = request.user
    chats = user.chats
    context["chats"] = chats
    return render(request, 'core/index.html', context)
