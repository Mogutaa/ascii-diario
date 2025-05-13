from flask import Blueprint, request, render_template, redirect, url_for
from auth import login_required
from config import Config
from pymongo import MongoClient
import re
import uuid
import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

client = MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME]
posts_collection = db.posts

@admin_bp.route('/console')
@login_required
def admin_console():
    return render_template('admin_console.html')

@admin_bp.route('/newpost', methods=['POST'])
@login_required
def new_post():
    if request.method == 'POST':
        content = request.form['content']
        ascii_images = []
        
        ascii_blocks = re.findall(r'```(.*?)```', content, re.DOTALL)
        for idx, block in enumerate(ascii_blocks):
            content = content.replace(f'```{block}```', f'[ASCII_IMAGE_{idx}]')
            ascii_images.append({
                'name': f'ascii_{uuid.uuid4().hex[:6]}.txt',
                'content': block.strip(),
                'position': f'inline_{idx}'
            })
        
        post_data = {
            'title': request.form['title'],
            'type': request.form['type'],
            'content': content,
            'ascii_images': ascii_images,
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()],
            'date': datetime.datetime.utcnow(),
            'author': 'admin'
        }
        
        posts_collection.insert_one(post_data)
    return redirect(url_for('admin.admin_console'))