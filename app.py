from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os
DATABASE = os.environ.get('DATABASE_PATH', 'tasks.db')

app = Flask(__name__)
DATABASE = 'tasks.db'

def get_db():
    """Подключение к базе данных"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация базы данных"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Получить все задачи"""
    try:
        conn = get_db()
        cursor = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'success': True, 'tasks': tasks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Создать новую задачу"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'success': False, 'error': 'Название задачи обязательно'}), 400
        
        title = data['title'].strip()
        description = data.get('description', '').strip()
        
        if len(title) > 200:
            return jsonify({'success': False, 'error': 'Название слишком длинное'}), 400
        
        conn = get_db()
        cursor = conn.execute(
            'INSERT INTO tasks (title, description) VALUES (?, ?)',
            (title, description)
        )
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Задача создана',
            'task_id': task_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Обновить задачу"""
    try:
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return jsonify({'success': False, 'error': 'Задача не найдена'}), 404
        
        title = data.get('title', task['title']).strip()
        description = data.get('description', task['description']).strip()
        completed = data.get('completed', task['completed'])
        
        conn.execute(
            'UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?',
            (title, description, 1 if completed else 0, task_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Задача обновлена'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Удалить задачу"""
    try:
        conn = get_db()
        cursor = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return jsonify({'success': False, 'error': 'Задача не найдена'}), 404
        
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Задача удалена'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """Переключить статус задачи"""
    try:
        conn = get_db()
        cursor = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return jsonify({'success': False, 'error': 'Задача не найдена'}), 404
        
        new_status = 0 if task['completed'] else 1
        conn.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'completed': bool(new_status)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("🚀 Запуск Task Manager на http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
