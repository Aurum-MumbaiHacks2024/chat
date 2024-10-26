from huggingface_hub import InferenceClient
from .models import *
import markdown2
from bs4 import BeautifulSoup
import re

def llm_response(messageid, messages):
    message_history = []
    for m in messages:
        message = {}
        message["role"] = m.sender
        message["content"] = m.content
        message_history.append(message)
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
        assistant_message = Message.objects.get(id=messageid)
        response_message = parse_markdown(response.choices[0].message.content)
        assistant_message.content = response.choices[0].message.content
        assistant_message.content_html = response_message
        assistant_message.save()
    except:
        assistant_message = Message.objects.get(id=messageid)
        assistant_message.sender = "system"
        assistant_message.content = "Something went wrong while generating response"
        assistant_message.save()

def parse_markdown(markdown_text):
    # Convert Markdown to HTML
    html_content = markdown2.markdown(markdown_text, extras=["fenced-code-blocks", "tables"])
    soup = BeautifulSoup(html_content, 'html.parser')

    # Add DaisyUI classes to various HTML elements
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        tag['class'] = tag.get('class', []) + ['font-bold']
        if tag.name == 'h1':
            tag['class'] += ['text-3xl', 'text-gray-900', 'dark:text-white']
        elif tag.name == 'h2':
            tag['class'] += ['text-2xl', 'text-gray-900', 'dark:text-white']
        elif tag.name == 'h3':
            tag['class'] += ['text-xl', 'text-gray-900', 'dark:text-white']
        elif tag.name == 'h4':
            tag['class'] += ['text-lg', 'text-gray-900', 'dark:text-white']
        elif tag.name == 'h5':
            tag['class'] += ['text-base', 'text-gray-900', 'dark:text-white']
        elif tag.name == 'h6':
            tag['class'] += ['text-sm', 'text-gray-900', 'dark:text-white']

        # Add an ID to the header for anchor links
        if not tag.get('id'):
            # Create an ID from the header text
            header_id = re.sub(r'\W+', '-', tag.get_text(strip=True)).lower()
            tag['id'] = header_id

    for tag in soup.find_all('p'):
        tag['class'] = tag.get('class', []) + ['mb-2', 'text-gray-900', 'dark:text-white']

    for tag in soup.find_all('ul'):
        tag['class'] = tag.get('class', []) + ['list-disc', 'ml-5', 'text-gray-900', 'dark:text-white']

    for tag in soup.find_all('ol'):
        tag['class'] = tag.get('class', []) + ['list-decimal', 'ml-5', 'text-gray-900', 'dark:text-white']

    for tag in soup.find_all('code'):
        tag['class'] = tag.get('class', []) + ['px-1', 'text-gray-900', 'dark:text-white']

    for tag in soup.find_all('pre'):
        # Create the mockup-code div
        mockup_code_div = soup.new_tag('div', **{'class': 'mockup-code'})
        
        # Add the DaisyUI classes to the pre tag
        tag['class'] = tag.get('class', []) + ['rounded', 'p-4', 'my-4', 'overflow-auto', 'text-gray-900', 'dark:text-white', 'bg-gray-200', 'dark:bg-gray-800']
        
        code_tag = tag.find('code')
        if code_tag:
            code_tag.extract()
            tag.append(code_tag)
        tag.wrap(mockup_code_div)

    for tag in soup.find_all('table'):
        tag['class'] = tag.get('class', []) + ['table-auto', 'w-full', 'my-4', 'border-collapse', 'text-gray-900', 'dark:text-white']
        for th in tag.find_all('th'):
            th['class'] = th.get('class', []) + ['border', 'px-4', 'py-2', 'text-gray-900', 'dark:text-white']
        for td in tag.find_all('td'):
            td['class'] = td.get('class', []) + ['border', 'px-4', 'py-2', 'text-gray-900', 'dark:text-white']

    for tag in soup.find_all('a'):
        tag['class'] = tag.get('class', []) + ['hover:text-blue-500', 'text-gray-900', 'dark:text-white']

    return str(soup)