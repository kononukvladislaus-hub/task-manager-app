import os
import json
import pytest
import sqlite3
from app import app

@pytest.fixture
def client():
    # Переключаем базу в оперативную память для абсолютной изоляции и скорости тестов
    test_db_path = ':memory:'
    app.config['TESTING'] = True
    
    # Подменяем функцию получения БД на тестовую
    def get_test_db():
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Инициализируем схему в памяти
    conn = sqlite3.connect(test_db_path)
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

    # Патчим оригинальный метод в app
    import app as app_module
    original_get_db = app_module.get_db
    app_module.get_db = get_test_db

    with app.test_client() as client:
        yield client

    # Возвращаем всё назад
    app_module.get_db = original_get_db

def test_get_tasks_empty(client):
    """Проверка: Изначально список задач пуст"""
    response = client.get('/api/tasks')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['tasks']) == 0

def test_create_task_success(client):
    """Проверка: Успешное добавление задачи"""
    payload = {'title': 'Купить хлеб', 'description': 'Ржаной'}
    response = client.post('/api/tasks', json=payload)
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['success'] is True
    assert 'task_id' in data

def test_create_task_invalid(client):
    """Проверка валидации: Пустое название возвращает 400"""
    response = client.post('/api/tasks', json={'title': ''})
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data['success'] is False
