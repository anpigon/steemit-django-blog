from django.shortcuts import render
from datetime import datetime
import markdown
import requests
import json
md = markdown.Markdown([
    'markdown.extensions.extra',
    'markdown.extensions.codehilite'
])
URL = 'https://api.steemit.com'
USERNAME = 'bbooaae'
def parse_time(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
def post_list(request, limit=20):
    start_entry_id = int(request.GET.get('next', '0'))
    data = '''{
        "jsonrpc": "2.0",
        "method": "follow_api.get_blog",
        "params": {"account": "%s", "start_entry_id": %i, "limit": %i},
        "id": 1
    }''' % (USERNAME, start_entry_id, limit + 1)
    response = requests.post(URL, data=data)
    posts = []
    if response.status_code == 200:
        data = json.loads(response.text)
        blogs = data['result']['blog']
        for blog in blogs:
            entry_id = blog['entry_id']
            blog = blog['comment']
            html = md.convert(blog['body'])
            post = {
                'title': blog['title'],
                'author': blog['author'],
                'permlink': blog['permlink'],
                'created': parse_time(blog['created']),
                'body': html[:200],
                }
            posts.append(post)
    if len(posts) < limit:
        entry_id = 0
    posts = posts[:limit]
    return render(request, 'blog/post_list.html', {'posts': posts, 'next': entry_id })
def post_detail(request, author='', permlink=''):
    data = '''{
         "jsonrpc": "2.0",
         "method": "condenser_api.get_content",
         "params": ["%s", "%s"],
         "id": 1
    }''' %(author, permlink)
    response = requests.post(URL, data=data)
    post = {}
    if response.status_code == 200:
        data = json.loads(response.text)
        post = data['result']
        post['body'] = md.convert(post['body'])
        post['created'] = parse_time(post['created'])
    return render(request, 'blog/post_detail.html', { 'post': post })
