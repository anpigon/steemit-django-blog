from django.shortcuts import render
from datetime import datetime
import requests
import json
import markdown
import re

md = markdown.Markdown(['markdown.extensions.extra', 'markdown.extensions.codehilite'])

URL = 'https://api.steemit.com'
USERNAME = 'anpigon' # 스팀잇 아이디

def parse_time(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

# 게시글 리스트
def post_list(request, limit=20):

    start_entry_id = int(request.GET.get('next', '0'))

    data = '''{
        "jsonrpc": "2.0",
        "method": "follow_api.get_blog",
        "params": {"account": "%s", "start_entry_id": %i, "limit": %i},
        "id": 1
    }''' % (USERNAME, start_entry_id, limit + 1)
    response = requests.post(URL, data=data)

    posts = [] # 게시글 목록
    if response.status_code == 200: # 응답이 성공이라면
        data = json.loads(response.text) # JSON 파싱

        blogs = data['result']['blog']
        for blog in blogs: # 리스트에서 필요한 데이터만 가져오기
            entry_id = blog['entry_id']
            blog = blog['comment']
            # replaced = re.sub(r'^https?://([a-z0-9-]+\.)+[a-z0-9]{2,4}.*$', '', blog['body'])
            # ^(https?):\/\/([^:\/\s]+)(:([^\/]*))?((\/[^\s/\/]+)*)?\/([^#\s\?]*)(\?([^#\s]*))?(#(\w*))?$
            replaced = re.sub(r'(^https?://([a-zA-Z0-9][a-zA-Z0-9_-]+([.][a-zA-Z0-9][a-zA-Z0-9_-]+){1,2}(/[a-zA-Z0-9][a-zA-Z0-9_-]*)+)[.](png|PNG|jpg|JPG|jpeg|JPEG|bmp|BMP|gif|GIF))', r'<img src="\1">', blog['body'])
            html = md.convert(replaced) # 마크다운을 HTML로 변환
            post = {
                'title': blog['title'],
                'author': blog['author'],
                'permlink': blog['permlink'],
                'created': parse_time(blog['created']),
                'body': html[:200], # 길이 200으로 자르기
                }
            posts.append(post)

    if len(posts) < limit:
        entry_id = 0
    posts = posts[:limit]

    return render(request, 'blog/post_list.html', {'posts': posts, 'next': entry_id })

def post_detail(request, author='', permlink=''):
    # 스팀잇에서 게시글 본문 가져오기
    data = '''{
        "jsonrpc": "2.0",
        "method": "condenser_api.get_content",
        "params": ["%s", "%s"],
        "id": 1
    }''' %(author, permlink)
    response = requests.post(URL, data=data)

    post = {}
    if response.status_code == 200: # 응답이 성공이라면
        data = json.loads(response.text) # JSON 파싱
        post = data['result']
        # post['body'] = markdown.markdown(post['body'], ['markdown.extensions.extra'])
        replaced = re.sub(r'(^https?://([a-zA-Z0-9][a-zA-Z0-9_-]+([.][a-zA-Z0-9][a-zA-Z0-9_-]+){1,2}(/[a-zA-Z0-9][a-zA-Z0-9_-]*)+)[.](png|PNG|jpg|JPG|jpeg|JPEG|bmp|BMP|gif|GIF))', r'<img src="\1">', post['body'])
        post['body'] = md.convert(replaced)
        post['created'] = parse_time(post['created'])

    return render(request, 'blog/post_detail.html', { 'post': post })
