let currentFilter = 'all';
let tasks = [];

// Загрузка задач при загрузке страницы
document.addEventListener('DOMContentLoaded', loadTasks);

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        
        if (data.success) {
            tasks = data.tasks;
            renderTasks();
            updateStats();
        } else {
            showError('Ошибка загрузки задач: ' + data.error);
        }
    } catch (error) {
        showError('Ошибка соединения с сервером');
        console.error('Error:', error);
    }
}

function renderTasks() {
    const tasksList = document.getElementById('tasksList');
    
    let filteredTasks = tasks;
    if (currentFilter === 'active') {
        filteredTasks = tasks.filter(task => !task.completed);
    } else if (currentFilter === 'completed') {
        filteredTasks = tasks.filter(task => task.completed);
    }
    
    if (filteredTasks.length === 0) {
        tasksList.innerHTML = `
            <div class="empty-state">
                <p>📭 Нет задач для отображения</p>
                <p>Добавьте новую задачу выше!</p>
            </div>
        `;
        return;
    }
    
    tasksList.innerHTML = filteredTasks.map(task => `
        <div class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}">
            <input type="checkbox" class="task-checkbox" 
                   ${task.completed ? 'checked' : ''} 
                   onchange="toggleTask(${task.id})">
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.title)}</div>
                ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                <div class="task-date">Создано: ${formatDate(task.created_at)}</div>
            </div>
            <div class="task-actions">
                <button class="edit-btn" onclick="editTask(${task.id})">✏️</button>
                <button class="delete-btn" onclick="deleteTask(${task.id})">🗑️</button>
            </div>
        </div>
    `).join('');
}

async function addTask() {
    const titleInput = document.getElementById('taskTitle');
    const descInput = document.getElementById('taskDescription');
    
    const title = titleInput.value.trim();
    const description = descInput.value.trim();
    
    if (!title) {
        showError('Введите название задачи');
        return;
    }
    
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, description })
        });
        
        const data = await response.json();
        
        if (data.success) {
            titleInput.value = '';
            descInput.value = '';
            await loadTasks();
        } else {
            showError('Ошибка создания задачи: ' + data.error);
        }
    } catch (error) {
        showError('Ошибка соединения с сервером');
        console.error('Error:', error);
    }
}

async function toggleTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/toggle`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadTasks();
        } else {
            showError('Ошибка обновления задачи');
        }
    } catch (error) {
        showError('Ошибка соединения с сервером');
        console.error('Error:', error);
    }
}

async function deleteTask(taskId) {
    if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadTasks();
        } else {
            showError('Ошибка удаления задачи');
        }
    } catch (error) {
        showError('Ошибка соединения с сервером');
        console.error('Error:', error);
    }
}

async function editTask(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    const newTitle = prompt('Редактировать название:', task.title);
    if (newTitle === null) return;
    if (!newTitle.trim()) {
        alert('Название не может быть пустым');
        return;
    }
    
    const newDescription = prompt('Редактировать описание:', task.description || '');
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: newTitle.trim(),
                description: newDescription ? newDescription.trim() : '',
                completed: task.completed
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadTasks();
        } else {
            showError('Ошибка обновления задачи: ' + data.error);
        }
    } catch (error) {
        showError('Ошибка соединения с сервером');
        console.error('Error:', error);
    }
}

function filterTasks(filter) {
    currentFilter = filter;
    
    // Обновление активной кнопки
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    renderTasks();
}

function updateStats() {
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    
    document.getElementById('totalTasks').textContent = `Всего: ${total}`;
    document.getElementById('completedTasks').textContent = `Выполнено: ${completed}`;
}

function showError(message) {
    // Создаем или получаем элемент ошибки
    let errorDiv = document.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        document.querySelector('.task-form').prepend(errorDiv);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Добавление задачи по Enter
document.getElementById('taskTitle').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        addTask();
    }
});
