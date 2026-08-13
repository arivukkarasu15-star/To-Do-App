let tasks = [];
let activeFilters = { category: 'all', search: '' };
let editingTaskId = null;
let deletingTaskId = null;

const escapeHtml = str => str ? str.replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])) : '';

function showToast(msg, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = `<i class="fa-solid fa-circle-${type === 'success' ? 'check' : 'xmark'}"></i> <span>${msg}</span>`;
    container.appendChild(el);
    setTimeout(() => el.remove(), 2500);
}

// Global API Object
const api = {
    async request(url, method = 'GET', data = null) {
        try {
            const options = { method };
            if (data) {
                options.headers = { 'Content-Type': 'application/json' };
                options.body = JSON.stringify(data);
            }
            const res = await fetch(url, options);
            return res.ok ? await res.json() : null;
        } catch (err) {
            console.error("API error:", err);
            return null;
        }
    },
    async get() {
        const data = await this.request('/api/tasks');
        tasks = data || [];
        render();
    },
    async save(taskData) {
        const url = editingTaskId ? `/api/tasks/${editingTaskId}` : '/api/tasks';
        const method = editingTaskId ? 'PUT' : 'POST';

        if (editingTaskId) {
            const existing = tasks.find(t => t.id === editingTaskId);
            taskData.status = existing ? existing.status : 'active';
        }

        if (await this.request(url, method, taskData)) {
            showToast(editingTaskId ? 'Task updated' : 'Task created');
            closeModal();
            this.get();
        }
    },
    async toggle(id, currentStatus) {
        const nextStatus = currentStatus === 'completed' ? 'active' : 'completed';
        if (await this.request(`/api/tasks/${id}`, 'PUT', { status: nextStatus })) {
            this.get();
        }
    },
    async delete(id) {
        if (await this.request(`/api/tasks/${id}`, 'DELETE')) {
            showToast('Task deleted', 'danger');
            this.get();
        }
    }
};

// UI Render Engine
function render() {
    const search = activeFilters.search.toLowerCase();
    const filtered = tasks.filter(t =>
        (activeFilters.category === 'all' || t.category.toLowerCase() === activeFilters.category.toLowerCase()) &&
        (t.title.toLowerCase().includes(search) || (t.description && t.description.toLowerCase().includes(search)))
    );

    const active = filtered.filter(t => t.status === 'active');
    const completed = filtered.filter(t => t.status === 'completed');

    const activeBadge = document.getElementById('active-count-badge');
    const completedBadge = document.getElementById('completed-count-badge');
    const statCompleted = document.getElementById('stat-completed');
    const statActive = document.getElementById('stat-active');
    const progressText = document.getElementById('progress-percentage');
    const progressBar = document.getElementById('progress-bar-fill');

    if (activeBadge) activeBadge.textContent = active.length;
    if (completedBadge) completedBadge.textContent = completed.length;

    const totalCount = tasks.length;
    const completedCount = tasks.filter(t => t.status === 'completed').length;
    if (statCompleted) statCompleted.textContent = completedCount;
    if (statActive) statActive.textContent = totalCount - completedCount;

    const pct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
    if (progressText) progressText.textContent = `${pct}%`;
    if (progressBar) progressBar.style.width = `${pct}%`;

    const buildCard = t => {
        const isDone = t.status === 'completed';

        return `
            <div class="task-card">
                <div class="task-card-header">
                    <label class="task-checkbox-container">
                        <input type="checkbox" ${isDone ? 'checked' : ''} onchange="api.toggle(${t.id}, '${t.status}')">
                        <span class="custom-checkbox"><i class="fa-solid fa-check"></i></span>
                        <span class="task-title">${escapeHtml(t.title)}</span>
                    </label>
                    <div class="task-actions">
                        <button class="action-btn" onclick="openEdit(${t.id})"><i class="fa-solid fa-pen"></i></button>
                        <button class="action-btn delete-btn" onclick="openDeleteModal(${t.id})" aria-label="Delete task"><i class="fa-solid fa-trash-can"></i></button>
                    </div>
                </div>
                ${t.description ? `<p class="task-desc">${escapeHtml(t.description)}</p>` : ''}
                <div class="task-metadata">
                    <span class="meta-tag"><i class="fa-solid fa-tag"></i> ${escapeHtml(t.category)}</span>
                </div>
            </div>
        `;
    };

    const activeList = document.getElementById('active-tasks-list');
    const completedList = document.getElementById('completed-tasks-list');

    if (activeList) {
        activeList.innerHTML = active.length ? active.map(buildCard).join('') : '<div class="empty-state"><h3>No pending tasks found</h3></div>';
    }
    if (completedList) {
        completedList.innerHTML = completed.length ? completed.map(buildCard).join('') : '<div class="empty-state"><h3>No completed tasks yet</h3></div>';
    }
}

function openEdit(id) {
    const t = tasks.find(x => x.id === id);
    if (!t) return;
    editingTaskId = id;

    const modalTitle = document.getElementById('modal-title');
    if (modalTitle) modalTitle.textContent = 'Edit Task';

    const titleEl = document.getElementById('task-title');
    const descEl = document.getElementById('task-desc');
    const catEl = document.getElementById('task-category');
    if (titleEl) titleEl.value = t.title;
    if (descEl) descEl.value = t.description || '';
    if (catEl) catEl.value = t.category;

    const modal = document.getElementById('task-modal');
    if (modal) modal.classList.add('open');
}

function openCreate() {
    editingTaskId = null;
    const modalTitle = document.getElementById('modal-title');
    if (modalTitle) modalTitle.textContent = 'Create New Task';
    const form = document.getElementById('task-form');
    if (form) form.reset();
    const modal = document.getElementById('task-modal');
    if (modal) modal.classList.add('open');
}

function closeModal() {
    const modal = document.getElementById('task-modal');
    if (modal) modal.classList.remove('open');
}

function openDeleteModal(id) {
    deletingTaskId = id;
    const modal = document.getElementById('delete-modal');
    if (modal) modal.classList.add('open');
}

function closeDeleteModal() {
    deletingTaskId = null;
    const modal = document.getElementById('delete-modal');
    if (modal) modal.classList.remove('open');
}

function confirmDelete() {
    if (deletingTaskId === null) return;
    const id = deletingTaskId;
    closeDeleteModal();
    api.delete(id);
}

// Setup Application Listeners — runs AFTER DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const btnOpen = document.getElementById('btn-open-modal');
    const btnClose = document.getElementById('btn-close-modal');
    const btnCancel = document.getElementById('btn-cancel-modal');
    const sidebarToggle = document.getElementById('sidebar-toggle-btn');
    const modal = document.getElementById('task-modal');
    const deleteModal = document.getElementById('delete-modal');
    const btnConfirmDelete = document.getElementById('btn-confirm-delete');
    const btnCancelDelete = document.getElementById('btn-cancel-delete');
    const form = document.getElementById('task-form');
    const searchInput = document.getElementById('search-input');

    if (btnOpen) btnOpen.onclick = openCreate;
    if (btnClose) btnClose.onclick = closeModal;
    if (btnCancel) btnCancel.onclick = closeModal;
    if (modal) modal.onclick = e => { if (e.target === modal) closeModal(); };
    if (btnConfirmDelete) btnConfirmDelete.onclick = confirmDelete;
    if (btnCancelDelete) btnCancelDelete.onclick = closeDeleteModal;
    if (deleteModal) deleteModal.onclick = e => { if (e.target === deleteModal) closeDeleteModal(); };

    document.onkeydown = e => {
        if (e.key === 'Escape') {
            closeModal();
            closeDeleteModal();
        }
    };

    if (form) {
        form.onsubmit = e => {
            e.preventDefault();
            const titleVal = document.getElementById('task-title').value.trim();
            const descVal = document.getElementById('task-desc').value.trim();
            const catVal = document.getElementById('task-category').value || 'Personal';

            if (!titleVal) return;

            api.save({ title: titleVal, description: descVal, category: catVal });
        };
    }

    if (sidebarToggle) {
        sidebarToggle.onclick = () => {
            const sidebar = document.getElementById('sidebar');
            if (sidebar) sidebar.classList.toggle('open');
        };
    }

    document.querySelectorAll('.filter-item').forEach(item => {
        item.onclick = () => {
            document.querySelectorAll('.filter-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');
            activeFilters.category = item.dataset.value;
            render();
        };
    });

    if (searchInput) {
        searchInput.oninput = e => {
            activeFilters.search = e.target.value;
            render();
        };
    }

    api.get();
});
