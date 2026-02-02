const API_BASE = ''
let ws = null
let isPaused = false
let currentView = 'dashboard'
let currentResourceTab = 'proxies'
let allTasks = [] // Store tasks for assignment dropdown
let allResources = { proxies: [], cards: [], emails: [], accounts: [] } // Store all resources

// Initialization

document.addEventListener('DOMContentLoaded', () => {
  initNavigation()
  initResourceTabs()
  initFilters()
  initSearch()
  initModals()
  initMonitorControls()

  // Load initial data
  loadDashboardData()
  refreshAllData()

  // Connect WebSocket
  connectWebSocket()

  // Refresh data periodically
  setInterval(refreshAllData, 30000)
})

// Landing page

function enterApp() {
  document.getElementById('landing').style.display = 'none'
  document.getElementById('appContainer').classList.add('active')
}

function checkInitialView() {}

// Navigation

function initNavigation() {
  // Main nav tabs
  document.querySelectorAll('.nav-tab').forEach((tab) => {
    tab.addEventListener('click', (e) => {
      e.preventDefault()
      const view = tab.dataset.view
      switchView(view)
      closeMobileMenu()
    })
  })

  // Bottom nav (mobile)
  document.querySelectorAll('.bottom-nav-item').forEach((item) => {
    item.addEventListener('click', (e) => {
      e.preventDefault()
      const view = item.dataset.view
      switchView(view)
      updateBottomNav(view)
    })
  })

  // Mobile menu toggle
  const navToggle = document.getElementById('navToggle')
  if (navToggle) {
    navToggle.addEventListener('click', toggleMobileMenu)
  }

  // Mobile menu overlay close
  const mobileOverlay = document.getElementById('mobileMenuOverlay')
  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', closeMobileMenu)
  }

  // Links that switch views
  document.querySelectorAll('[data-view]').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault()
      const view = link.dataset.view
      switchView(view)
      updateBottomNav(view)
    })
  })

  // Create button
  const createBtn = document.getElementById('createBtn')
  if (createBtn) {
    createBtn.addEventListener('click', () => {
      if (currentView === 'tasks' || currentView === 'dashboard') {
        showTaskModal()
      } else if (currentView === 'resources') {
        showResourceModal()
      }
    })
  }
}

function toggleMobileMenu() {
  const navCenter = document.querySelector('.nav-center')
  const overlay = document.getElementById('mobileMenuOverlay')
  const navToggle = document.getElementById('navToggle')

  navCenter?.classList.toggle('mobile-open')
  overlay?.classList.toggle('active')
  navToggle?.classList.toggle('active')

  // Prevent body scroll when menu is open
  document.body.style.overflow = navCenter?.classList.contains('mobile-open')
    ? 'hidden'
    : ''
}

function closeMobileMenu() {
  const navCenter = document.querySelector('.nav-center')
  const overlay = document.getElementById('mobileMenuOverlay')
  const navToggle = document.getElementById('navToggle')

  navCenter?.classList.remove('mobile-open')
  overlay?.classList.remove('active')
  navToggle?.classList.remove('active')

  // Restore body scroll
  document.body.style.overflow = ''
}

function updateBottomNav(view) {
  document.querySelectorAll('.bottom-nav-item').forEach((item) => {
    item.classList.remove('active')
    if (item.dataset.view === view) {
      item.classList.add('active')
    }
  })
}

function switchView(view) {
  currentView = view

  // Update nav tabs
  document
    .querySelectorAll('.nav-tab')
    .forEach((t) => t.classList.remove('active'))
  document
    .querySelector(`.nav-tab[data-view="${view}"]`)
    ?.classList.add('active')

  // Update bottom nav
  updateBottomNav(view)

  // Update views
  document
    .querySelectorAll('.view')
    .forEach((v) => v.classList.remove('active'))
  document.getElementById(`${view}View`)?.classList.add('active')

  // Refresh data for view
  if (view === 'tasks') loadTasks()
  if (view === 'resources') refreshResourceTab()
  if (view === 'monitor') scrollActivityLogToBottom()
}

function switchToResourceTab(type) {
  switchView('resources')
  setTimeout(() => {
    document
      .querySelectorAll('.resource-tab')
      .forEach((t) => t.classList.remove('active'))
    document
      .querySelector(`.resource-tab[data-tab="${type}"]`)
      ?.classList.add('active')
    document
      .querySelectorAll('.resource-content')
      .forEach((c) => c.classList.remove('active'))
    document.getElementById(`${type}Tab`)?.classList.add('active')
    currentResourceTab = type
    refreshResourceTab()
  }, 100)
}

// Resource Tabs

function initResourceTabs() {
  document.querySelectorAll('.resource-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      document
        .querySelectorAll('.resource-tab')
        .forEach((t) => t.classList.remove('active'))
      tab.classList.add('active')

      const tabName = tab.dataset.tab
      currentResourceTab = tabName

      document
        .querySelectorAll('.resource-content')
        .forEach((c) => c.classList.remove('active'))
      document.getElementById(`${tabName}Tab`)?.classList.add('active')

      refreshResourceTab()
    })
  })
}

function refreshResourceTab() {
  switch (currentResourceTab) {
    case 'proxies':
      loadProxies()
      break
    case 'cards':
      loadCards()
      break
    case 'emails':
      loadEmails()
      break
    case 'accounts':
      loadAccounts()
      break
  }
}

function showResourceModal() {
  switch (currentResourceTab) {
    case 'proxies':
      showProxyModal()
      break
    case 'cards':
      showCardModal()
      break
    case 'emails':
      showEmailModal()
      break
    case 'accounts':
      showAccountModal()
      break
  }
}

// Filters

function initFilters() {
  // Filter pills
  document.querySelectorAll('.filter-pills .pill').forEach((pill) => {
    pill.addEventListener('click', () => {
      document
        .querySelectorAll('.filter-pills .pill')
        .forEach((p) => p.classList.remove('active'))
      pill.classList.add('active')
      loadTasks(pill.dataset.filter)
    })
  })

  // Status filter select
  const taskStatusFilter = document.getElementById('taskStatusFilter')
  if (taskStatusFilter) {
    taskStatusFilter.addEventListener('change', () => {
      loadTasks(taskStatusFilter.value)
    })
  }

  // Proxy status filter
  const proxyStatusFilter = document.getElementById('proxyStatusFilter')
  if (proxyStatusFilter) {
    proxyStatusFilter.addEventListener('change', loadProxies)
  }

  // Card status filter
  const cardStatusFilter = document.getElementById('cardStatusFilter')
  if (cardStatusFilter) {
    cardStatusFilter.addEventListener('change', loadCards)
  }

  // Email status filter
  const emailStatusFilter = document.getElementById('emailStatusFilter')
  if (emailStatusFilter) {
    emailStatusFilter.addEventListener('change', loadEmails)
  }

  // Account status filter
  const accountStatusFilter = document.getElementById('accountStatusFilter')
  if (accountStatusFilter) {
    accountStatusFilter.addEventListener('change', loadAccounts)
  }
}

// Search

function initSearch() {
  const searchInput = document.getElementById('globalSearch')
  if (searchInput) {
    searchInput.addEventListener(
      'input',
      debounce((e) => {
        const query = e.target.value.toLowerCase()
        // Implement search functionality
      }, 300),
    )
  }
}

// Modals

function initModals() {
  const overlay = document.getElementById('modalOverlay')
  if (overlay) {
    overlay.addEventListener('click', closeAllModals)
  }

  // Close on escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllModals()
    }
  })
}

function openModal(modalId) {
  document.getElementById('modalOverlay')?.classList.add('active')
  document.getElementById(modalId)?.classList.add('active')
}

function closeModal(modalId) {
  document.getElementById('modalOverlay')?.classList.remove('active')
  document.getElementById(modalId)?.classList.remove('active')
}

function closeAllModals() {
  document.getElementById('modalOverlay')?.classList.remove('active')
  document
    .querySelectorAll('.modal')
    .forEach((m) => m.classList.remove('active'))
}

// Monitor Controls

function initMonitorControls() {
  const clearBtn = document.getElementById('clearLogs')
  if (clearBtn) {
    clearBtn.addEventListener('click', clearActivityLog)
  }

  const pauseBtn = document.getElementById('pauseLogs')
  if (pauseBtn) {
    pauseBtn.addEventListener('click', togglePauseLogs)
  }
}

function clearActivityLog() {
  const log = document.getElementById('activityLog')
  if (log) {
    log.innerHTML = `
            <div class="log-item info">
                <span class="log-time">${getTimeString()}</span>
                <span class="log-text">Activity log cleared</span>
            </div>
        `
  }
}

function togglePauseLogs() {
  isPaused = !isPaused
  const pauseBtn = document.getElementById('pauseLogs')
  if (pauseBtn) {
    pauseBtn.innerHTML = isPaused
      ? '<i class="fas fa-play"></i>'
      : '<i class="fas fa-pause"></i>'
    pauseBtn.title = isPaused ? 'Resume' : 'Pause'
  }
}

function scrollActivityLogToBottom() {
  const log = document.getElementById('activityLog')
  if (log) {
    log.scrollTop = log.scrollHeight
  }
}

// API Functions

async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

// Data Loading

async function loadDashboardData() {
  try {
    const [tasks, proxies, cards, emails, accounts] = await Promise.all([
      apiRequest('/api/tasks/'),
      apiRequest('/api/resources/proxies/'),
      apiRequest('/api/resources/cards/'),
      apiRequest('/api/resources/emails/'),
      apiRequest('/api/resources/accounts/'),
    ])

    allTasks = tasks
    allResources = { proxies, cards, emails, accounts }
    updateDashboardStats(tasks, proxies, cards, emails, accounts)
    updateHeroStats(tasks, proxies, cards, emails, accounts)
    updateActiveTasks(tasks)
    updateRecentErrors(tasks)
  } catch (error) {
    console.error('Error loading dashboard:', error)
  }
}

function updateDashboardStats(tasks, proxies, cards, emails, accounts) {
  // Task stats
  document.getElementById('totalTasks').textContent = tasks.length
  document.getElementById('runningTasks').textContent = tasks.filter(
    (t) => t.status === 'running',
  ).length
  document.getElementById('completedTasks').textContent = tasks.filter(
    (t) => t.status === 'completed',
  ).length

  const totalErrors = tasks.reduce((sum, t) => sum + (t.errors?.length || 0), 0)
  document.getElementById('totalErrors').textContent = totalErrors

  // Resource stats
  updateResourceStats('proxies', proxies)
  updateResourceStats('cards', cards)
  updateResourceStats('emails', emails)
  updateResourceStats('accounts', accounts)

  // Monitor stats
  document.getElementById('monitorRunning').textContent = tasks.filter(
    (t) => t.status === 'running',
  ).length
  document.getElementById('monitorQueued').textContent = tasks.filter(
    (t) => t.status === 'pending',
  ).length
}

function updateResourceStats(type, items) {
  const total = items.length
  const available = items.filter((i) => i.status === 'available').length
  const inUse = items.filter((i) => i.status === 'in_use').length

  document.getElementById(`${type}Total`).textContent = total
  document.getElementById(`${type}Available`).textContent = available
  document.getElementById(`${type}InUse`).textContent = inUse
}

function updateHeroStats(tasks, proxies, cards, emails, accounts) {
  const heroTasks = document.getElementById('heroTasks')
  const heroResources = document.getElementById('heroResources')

  if (heroTasks) heroTasks.textContent = tasks.length
  if (heroResources) {
    heroResources.textContent =
      proxies.length + cards.length + emails.length + accounts.length
  }
}

function updateActiveTasks(tasks) {
  const container = document.getElementById('activeTasksList')
  const activeTasks = tasks.filter(
    (t) => t.status === 'running' || t.status === 'pending',
  )

  if (activeTasks.length === 0) {
    container.innerHTML = `
            <div class="empty-state-small">
                <i class="fas fa-inbox"></i>
                <p>No active tasks</p>
            </div>
        `
    return
  }

  container.innerHTML = activeTasks
    .slice(0, 5)
    .map(
      (task) => `
        <div class="active-task-item">
            <div class="task-status-indicator ${task.status}"></div>
            <div class="active-task-info">
                <div class="active-task-name">${escapeHtml(task.name)}</div>
                <div class="active-task-stage">${task.stage || 'Starting...'}</div>
            </div>
            <span class="task-badge ${task.status}">${task.status}</span>
        </div>
    `,
    )
    .join('')
}

function updateRecentErrors(tasks) {
  const container = document.getElementById('errorsList')
  const allErrors = []

  tasks.forEach((task) => {
    if (task.errors) {
      task.errors.forEach((error) => {
        allErrors.push({
          ...error,
          taskName: task.name,
          taskId: task.id,
        })
      })
    }
  })

  if (allErrors.length === 0) {
    container.innerHTML = `
            <div class="empty-state-small">
                <i class="fas fa-check-circle"></i>
                <p>No recent errors</p>
            </div>
        `
    return
  }

  container.innerHTML = allErrors
    .slice(0, 5)
    .map(
      (error) => `
        <div class="error-item">
            <i class="fas fa-exclamation-circle"></i>
            <div class="error-info">
                <div class="error-message">${escapeHtml(error.message || 'Unknown error')}</div>
                <div class="error-time">${error.taskName}</div>
            </div>
        </div>
    `,
    )
    .join('')
}

async function refreshAllData() {
  loadDashboardData()
}

// Tasks

async function loadTasks(statusFilter = '') {
  try {
    let url = '/api/tasks/'
    if (statusFilter) {
      url += `?status=${statusFilter}`
    }

    const tasks = await apiRequest(url)
    renderTasks(tasks)
  } catch (error) {
    console.error('Error loading tasks:', error)
  }
}

function renderTasks(tasks) {
  const container = document.getElementById('tasksList')
  allTasks = tasks // Update stored tasks

  if (tasks.length === 0) {
    container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-tasks"></i>
                </div>
                <h3>No tasks yet</h3>
                <p>Create your first task to get started</p>
                <button class="btn btn-primary" onclick="showTaskModal()">
                    <i class="fas fa-plus"></i> Create Task
                </button>
            </div>
        `
    return
  }

  container.innerHTML = tasks
    .map(
      (task) => `
        <div class="task-item" data-id="${task.id}" onclick="showTaskDetails('${task.id}')">
            <div class="task-status-indicator ${task.status}"></div>
            <div class="task-info">
                <div class="task-name">${escapeHtml(task.name)}</div>
                <div class="task-description">${escapeHtml(task.description || 'No description')}</div>
                <div class="task-resources-summary">
                    ${task.resources?.proxy_ids?.length ? `<span class="resource-tag"><i class="fas fa-shield-alt"></i> ${task.resources.proxy_ids.length}</span>` : ''}
                    ${task.resources?.card_ids?.length ? `<span class="resource-tag"><i class="fas fa-credit-card"></i> ${task.resources.card_ids.length}</span>` : ''}
                    ${task.resources?.email_ids?.length ? `<span class="resource-tag"><i class="fas fa-envelope"></i> ${task.resources.email_ids.length}</span>` : ''}
                    ${task.resources?.account_ids?.length ? `<span class="resource-tag"><i class="fas fa-user"></i> ${task.resources.account_ids.length}</span>` : ''}
                </div>
            </div>
            <div class="task-meta">
                ${
                  task.progress?.percentage > 0
                    ? `
                    <div class="task-progress-mini">
                        <div class="progress-bar-mini">
                            <div class="progress-fill-mini" style="width: ${task.progress.percentage}%"></div>
                        </div>
                        <span>${Math.round(task.progress.percentage)}%</span>
                    </div>
                `
                    : ''
                }
                <span class="task-badge ${task.status}">${task.status}</span>
            </div>
            <div class="task-actions" onclick="event.stopPropagation()">
                ${
                  task.status === 'pending' || task.status === 'paused'
                    ? `<button class="btn btn-sm btn-outline" onclick="startTask('${task.id}')" title="Start"><i class="fas fa-play"></i></button>`
                    : ''
                }
                ${
                  task.status === 'running'
                    ? `<button class="btn btn-sm btn-outline" onclick="pauseTask('${task.id}')" title="Pause"><i class="fas fa-pause"></i></button>`
                    : ''
                }
                ${
                  task.status === 'running' || task.status === 'paused'
                    ? `<button class="btn btn-sm btn-success" onclick="completeTask('${task.id}')" title="Complete"><i class="fas fa-check"></i></button>`
                    : ''
                }
                ${
                  task.status !== 'completed' &&
                  task.status !== 'cancelled' &&
                  task.status !== 'failed'
                    ? `<button class="btn btn-sm btn-warning" onclick="cancelTask('${task.id}')" title="Cancel"><i class="fas fa-ban"></i></button>`
                    : ''
                }
                <button class="btn btn-sm btn-outline" onclick="editTask('${task.id}')" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-ghost" onclick="deleteTask('${task.id}')" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `,
    )
    .join('')
}

function showTaskModal(taskId = null) {
  document.getElementById('taskForm').reset()
  document.getElementById('taskId').value = ''
  document.getElementById('taskModalTitle').textContent = taskId
    ? 'Edit Task'
    : 'Create Task'
  openModal('taskModal')
}

async function saveTask() {
  const taskId = document.getElementById('taskId').value
  const name = document.getElementById('taskName').value.trim()
  const description = document.getElementById('taskDescription').value.trim()

  if (!name) {
    showToast('Error', 'Task name is required', 'error')
    return
  }

  try {
    const data = { name, description: description || null }

    if (taskId) {
      await apiRequest(`/api/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Task updated', 'success')
    } else {
      await apiRequest('/api/tasks/', {
        method: 'POST',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Task created', 'success')
    }

    closeModal('taskModal')
    loadTasks()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to save task', 'error')
  }
}

async function startTask(taskId) {
  try {
    await apiRequest(`/api/tasks/${taskId}/start`, { method: 'POST' })
    showToast('Success', 'Task started', 'success')
    loadTasks()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to start task', 'error')
  }
}

async function pauseTask(taskId) {
  try {
    await apiRequest(`/api/tasks/${taskId}/pause`, { method: 'POST' })
    showToast('Success', 'Task paused', 'success')
    loadTasks()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to pause task', 'error')
  }
}

async function completeTask(taskId) {
  try {
    await apiRequest(`/api/tasks/${taskId}/complete`, { method: 'POST' })
    showToast('Success', 'Task marked as completed', 'success')
    loadTasks()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to complete task', 'error')
  }
}

async function cancelTask(taskId) {
  if (!confirm('Are you sure you want to cancel this task?')) return
  try {
    await apiRequest(`/api/tasks/${taskId}/cancel`, { method: 'POST' })
    showToast('Success', 'Task cancelled', 'success')
    loadTasks()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to cancel task', 'error')
  }
}

async function updateTaskProgress(taskId, percentage, stage = null) {
  try {
    let url = `/api/tasks/${taskId}/progress?percentage=${percentage}`
    if (stage) url += `&stage=${stage}`
    await apiRequest(url, { method: 'PUT' })
    loadTasks()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to update progress', 'error')
  }
}

async function addTaskError(taskId, errorMessage, errorCode = 'UNKNOWN') {
  try {
    await apiRequest(`/api/tasks/${taskId}/error`, {
      method: 'POST',
      body: JSON.stringify({ message: errorMessage, code: errorCode }),
    })
    loadTasks()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to add error', 'error')
  }
}

async function deleteTask(taskId) {
  if (!confirm('Are you sure you want to delete this task?')) return

  try {
    await apiRequest(`/api/tasks/${taskId}`, { method: 'DELETE' })
    showToast('Success', 'Task deleted', 'success')
    loadTasks()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to delete task', 'error')
  }
}

async function editTask(taskId) {
  try {
    const task = await apiRequest(`/api/tasks/${taskId}`)
    document.getElementById('taskId').value = task.id
    document.getElementById('taskName').value = task.name
    document.getElementById('taskDescription').value = task.description || ''
    document.getElementById('taskModalTitle').textContent = 'Edit Task'
    openModal('taskModal')
  } catch (error) {
    showToast('Error', 'Failed to load task', 'error')
  }
}

async function showTaskDetails(taskId) {
  try {
    const task = await apiRequest(`/api/tasks/${taskId}`)

    document.getElementById('detailTaskName').textContent = task.name
    document.getElementById('detailTaskDescription').textContent =
      task.description || 'No description'
    document.getElementById('detailTaskStatus').textContent = task.status
    document.getElementById('detailTaskStatus').className =
      `task-badge ${task.status}`
    document.getElementById('detailTaskProgress').style.width =
      `${task.progress?.percentage || 0}%`
    document.getElementById('detailTaskProgressText').textContent =
      `${Math.round(task.progress?.percentage || 0)}%`
    document.getElementById('detailTaskStage').textContent =
      task.progress?.stage || task.stage || '-'
    document.getElementById('detailTaskId').value = taskId

    // Render task controls based on status
    const controlsContainer = document.getElementById('taskDetailControls')
    let controlsHtml = ''

    if (task.status === 'pending' || task.status === 'paused') {
      controlsHtml += `<button class="btn btn-primary" onclick="startTask('${taskId}'); closeModal('taskDetailModal');"><i class="fas fa-play"></i> Start</button>`
    }
    if (task.status === 'running') {
      controlsHtml += `<button class="btn btn-warning" onclick="pauseTask('${taskId}'); closeModal('taskDetailModal');"><i class="fas fa-pause"></i> Pause</button>`
    }
    if (task.status === 'running' || task.status === 'paused') {
      controlsHtml += `<button class="btn btn-success" onclick="completeTask('${taskId}'); closeModal('taskDetailModal');"><i class="fas fa-check"></i> Complete</button>`
    }
    if (
      task.status !== 'completed' &&
      task.status !== 'cancelled' &&
      task.status !== 'failed'
    ) {
      controlsHtml += `<button class="btn btn-outline" onclick="cancelTask('${taskId}'); closeModal('taskDetailModal');"><i class="fas fa-ban"></i> Cancel</button>`
    }

    controlsContainer.innerHTML =
      controlsHtml || '<p class="text-muted">No actions available</p>'

    // Load assigned resources
    await loadTaskResources(task)

    // Load errors
    renderTaskErrors(task)

    openModal('taskDetailModal')
  } catch (error) {
    showToast('Error', 'Failed to load task details', 'error')
  }
}

function renderTaskErrors(task) {
  const container = document.getElementById('taskErrorsList')
  if (!task.errors || task.errors.length === 0) {
    container.innerHTML = '<p class="text-muted">No errors</p>'
    return
  }

  container.innerHTML = task.errors
    .map(
      (err) => `
    <div class="error-item">
      <i class="fas fa-exclamation-circle"></i>
      <div class="error-info">
        <div class="error-message">${escapeHtml(err.message)}</div>
        <div class="error-meta">${err.code || 'UNKNOWN'} - ${new Date(err.timestamp).toLocaleString()}</div>
      </div>
    </div>
  `,
    )
    .join('')
}

function editTaskFromDetail() {
  const taskId = document.getElementById('detailTaskId').value
  closeModal('taskDetailModal')
  editTask(taskId)
}

async function loadTaskResources(task) {
  const container = document.getElementById('taskResourcesList')
  const resources = []

  // Get resource details
  if (task.resources?.proxy_ids?.length) {
    for (const id of task.resources.proxy_ids) {
      try {
        const proxy = await apiRequest(`/api/resources/proxies/${id}`)
        resources.push({
          type: 'proxy',
          icon: 'fa-shield-alt',
          data: proxy,
          label: `${proxy.host}:${proxy.port}`,
        })
      } catch (e) {}
    }
  }
  if (task.resources?.card_ids?.length) {
    for (const id of task.resources.card_ids) {
      try {
        const card = await apiRequest(`/api/resources/cards/${id}`)
        resources.push({
          type: 'card',
          icon: 'fa-credit-card',
          data: card,
          label: `****${card.last_four}`,
        })
      } catch (e) {}
    }
  }
  if (task.resources?.email_ids?.length) {
    for (const id of task.resources.email_ids) {
      try {
        const email = await apiRequest(`/api/resources/emails/${id}`)
        resources.push({
          type: 'email',
          icon: 'fa-envelope',
          data: email,
          label: email.address,
        })
      } catch (e) {}
    }
  }
  if (task.resources?.account_ids?.length) {
    for (const id of task.resources.account_ids) {
      try {
        const account = await apiRequest(`/api/resources/accounts/${id}`)
        resources.push({
          type: 'account',
          icon: 'fa-user',
          data: account,
          label: `${account.platform}: ${account.username}`,
        })
      } catch (e) {}
    }
  }

  if (resources.length === 0) {
    container.innerHTML =
      '<p class="text-muted">No resources assigned to this task.</p>'
  } else {
    container.innerHTML = resources
      .map(
        (r) => `
      <div class="assigned-resource-item">
        <i class="fas ${r.icon}"></i>
        <span>${escapeHtml(r.label)}</span>
        <button class="btn btn-sm btn-ghost" onclick="releaseResourceFromTask('${r.type}', '${r.data.id}')" title="Release">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `,
      )
      .join('')
  }
}

async function releaseResourceFromTask(type, resourceId) {
  const typeMap = {
    proxy: 'proxies',
    card: 'cards',
    email: 'emails',
    account: 'accounts',
  }
  try {
    await apiRequest(`/api/resources/${typeMap[type]}/${resourceId}/release`, {
      method: 'POST',
    })
    showToast('Success', 'Resource released', 'success')
    const taskId = document.getElementById('detailTaskId').value
    const task = await apiRequest(`/api/tasks/${taskId}`)
    await loadTaskResources(task)
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to release resource', 'error')
  }
}

function showAssignResourceModal() {
  const taskId = document.getElementById('detailTaskId').value
  document.getElementById('assignTaskId').value = taskId
  loadAvailableResources()
  openModal('assignResourceModal')
}

async function loadAvailableResources() {
  try {
    const [proxies, cards, emails, accounts] = await Promise.all([
      apiRequest('/api/resources/proxies/?status=available'),
      apiRequest('/api/resources/cards/?status=available'),
      apiRequest('/api/resources/emails/?status=available'),
      apiRequest('/api/resources/accounts/?status=available'),
    ])

    renderAvailableResources(
      'modalAssignProxiesList',
      proxies,
      'proxy',
      (p) => `${p.host}:${p.port} (${p.proxy_type})`,
    )
    renderAvailableResources(
      'modalAssignCardsList',
      cards,
      'card',
      (c) => `****${c.last_four} - ${c.holder_name}`,
    )
    renderAvailableResources(
      'modalAssignEmailsList',
      emails,
      'email',
      (e) => e.address,
    )
    renderAvailableResources(
      'modalAssignAccountsList',
      accounts,
      'account',
      (a) => `${a.platform}: ${a.username}`,
    )
  } catch (error) {
    showToast('Error', 'Failed to load resources', 'error')
  }
}

function renderAvailableResources(containerId, items, type, labelFn) {
  const container = document.getElementById(containerId)
  if (items.length === 0) {
    container.innerHTML = '<p class="text-muted">No available resources</p>'
    return
  }
  container.innerHTML = items
    .map(
      (item) => `
    <label class="resource-checkbox">
      <input type="checkbox" name="assign_${type}" value="${item.id}">
      <span>${escapeHtml(labelFn(item))}</span>
    </label>
  `,
    )
    .join('')
}

async function assignSelectedResources() {
  const taskId = document.getElementById('assignTaskId').value

  const proxyIds = [
    ...document.querySelectorAll('input[name="assign_proxy"]:checked'),
  ].map((c) => c.value)
  const cardIds = [
    ...document.querySelectorAll('input[name="assign_card"]:checked'),
  ].map((c) => c.value)
  const emailIds = [
    ...document.querySelectorAll('input[name="assign_email"]:checked'),
  ].map((c) => c.value)
  const accountIds = [
    ...document.querySelectorAll('input[name="assign_account"]:checked'),
  ].map((c) => c.value)

  try {
    // Assign each resource individually to update status
    for (const id of proxyIds) {
      await apiRequest(`/api/resources/proxies/${id}/assign/${taskId}`, {
        method: 'POST',
      })
    }
    for (const id of cardIds) {
      await apiRequest(`/api/resources/cards/${id}/assign/${taskId}`, {
        method: 'POST',
      })
    }
    for (const id of emailIds) {
      await apiRequest(`/api/resources/emails/${id}/assign/${taskId}`, {
        method: 'POST',
      })
    }
    for (const id of accountIds) {
      await apiRequest(`/api/resources/accounts/${id}/assign/${taskId}`, {
        method: 'POST',
      })
    }

    showToast('Success', 'Resources assigned', 'success')
    closeModal('assignResourceModal')

    // Refresh task details
    const task = await apiRequest(`/api/tasks/${taskId}`)
    await loadTaskResources(task)
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to assign resources', 'error')
  }
}

// Proxies
async function loadProxies() {
  try {
    const statusFilter = document.getElementById('proxyStatusFilter')?.value
    let url = '/api/resources/proxies/'
    if (statusFilter) {
      url += `?status=${statusFilter}`
    }

    const proxies = await apiRequest(url)
    allResources.proxies = proxies
    renderProxies(proxies)
  } catch (error) {
    console.error('Error loading proxies:', error)
  }
}

function renderProxies(proxies) {
  const tbody = document.getElementById('proxiesTableBody')

  if (proxies.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 3rem; color: var(--gray-500);">
                    No proxies found. Add your first proxy.
                </td>
            </tr>
        `
    return
  }

  tbody.innerHTML = proxies
    .map(
      (proxy) => `
        <tr>
            <td><strong>${escapeHtml(proxy.host)}</strong></td>
            <td>${proxy.port}</td>
            <td><span class="status-badge">${proxy.proxy_type}</span></td>
            <td>${proxy.country || 'N/A'}${proxy.city ? `, ${proxy.city}` : ''}</td>
            <td><span class="status-badge ${proxy.status}">${proxy.status}</span></td>
            <td>${proxy.assigned_task_id ? 'Task ' + proxy.assigned_task_id.slice(0, 8) : '-'}</td>
            <td>
                <div class="task-actions">
                    <button class="btn btn-sm btn-outline" onclick="showProxyModal('${proxy.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${
                      proxy.status === 'available'
                        ? `
                        <button class="btn btn-sm btn-outline" onclick="showAssignModal('proxy', '${proxy.id}')" title="Assign to Task">
                            <i class="fas fa-link"></i>
                        </button>
                    `
                        : ''
                    }
                    ${
                      proxy.status === 'in_use'
                        ? `
                        <button class="btn btn-sm btn-outline" onclick="releaseResource('proxies', '${proxy.id}')" title="Release">
                            <i class="fas fa-unlink"></i>
                        </button>
                    `
                        : ''
                    }
                    <button class="btn btn-sm btn-ghost" onclick="deleteProxy('${proxy.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `,
    )
    .join('')
}

function showProxyModal(proxyId = null) {
  document.getElementById('proxyForm').reset()
  document.getElementById('proxyId').value = ''
  document.getElementById('proxyModalTitle').textContent = proxyId
    ? 'Edit Proxy'
    : 'Add Proxy'

  if (proxyId) {
    // Fetch and populate for edit mode
    editProxy(proxyId)
    return
  }

  openModal('proxyModal')
}

async function editProxy(proxyId) {
  try {
    const proxy = await apiRequest(`/api/resources/proxies/${proxyId}`)
    document.getElementById('proxyId').value = proxy.id
    document.getElementById('proxyHost').value = proxy.host
    document.getElementById('proxyPort').value = proxy.port
    document.getElementById('proxyType').value = proxy.proxy_type
    document.getElementById('proxyUsername').value = proxy.username || ''
    document.getElementById('proxyPassword').value = proxy.password || ''
    document.getElementById('proxyCountry').value = proxy.country || ''
    document.getElementById('proxyCity').value = proxy.city || ''
    document.getElementById('proxyModalTitle').textContent = 'Edit Proxy'
    openModal('proxyModal')
  } catch (error) {
    showToast('Error', 'Failed to load proxy', 'error')
  }
}

async function saveProxy() {
  const proxyId = document.getElementById('proxyId')?.value
  const data = {
    host: document.getElementById('proxyHost').value.trim(),
    port: parseInt(document.getElementById('proxyPort').value),
    proxy_type: document.getElementById('proxyType').value,
    username: document.getElementById('proxyUsername').value.trim() || null,
    password: document.getElementById('proxyPassword').value || null,
    country: document.getElementById('proxyCountry').value.trim() || null,
    city: document.getElementById('proxyCity').value.trim() || null,
  }

  if (!data.host || !data.port) {
    showToast('Error', 'Host and port are required', 'error')
    return
  }

  try {
    if (proxyId) {
      await apiRequest(`/api/resources/proxies/${proxyId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Proxy updated', 'success')
    } else {
      await apiRequest('/api/resources/proxies/', {
        method: 'POST',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Proxy added', 'success')
    }
    closeModal('proxyModal')
    loadProxies()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to save proxy', 'error')
  }
}

async function deleteProxy(proxyId) {
  if (!confirm('Delete this proxy?')) return

  try {
    await apiRequest(`/api/resources/proxies/${proxyId}`, { method: 'DELETE' })
    showToast('Success', 'Proxy deleted', 'success')
    loadProxies()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to delete proxy', 'error')
  }
}

// Bulk Proxy Import
function showBulkProxyModal() {
  document.getElementById('bulkProxyInput').value = ''
  document.getElementById('bulkProxyType').value = 'http'
  openModal('bulkProxyModal')
}

async function bulkImportProxies() {
  const input = document.getElementById('bulkProxyInput').value.trim()
  const proxyType = document.getElementById('bulkProxyType').value

  if (!input) {
    showToast('Error', 'Please enter proxy data', 'error')
    return
  }

  const lines = input.split('\n').filter((line) => line.trim())
  const proxies = []

  for (const line of lines) {
    const parts = line.trim().split(':')
    if (parts.length >= 2) {
      const proxy = {
        host: parts[0],
        port: parseInt(parts[1]),
        proxy_type: proxyType,
      }
      if (parts.length >= 4) {
        proxy.username = parts[2]
        proxy.password = parts[3]
      }
      proxies.push(proxy)
    }
  }

  if (proxies.length === 0) {
    showToast('Error', 'No valid proxies found', 'error')
    return
  }

  try {
    await apiRequest('/api/resources/proxies/bulk', {
      method: 'POST',
      body: JSON.stringify(proxies),
    })
    showToast('Success', `Imported ${proxies.length} proxies`, 'success')
    closeModal('bulkProxyModal')
    loadProxies()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to import proxies', 'error')
  }
}

// Generic assign/release functions for resources
function showAssignModal(resourceType, resourceId) {
  document.getElementById('quickAssignResourceType').value = resourceType
  document.getElementById('quickAssignResourceId').value = resourceId

  // Populate task dropdown
  const select = document.getElementById('quickAssignTaskSelect')
  select.innerHTML =
    '<option value="">Select a task...</option>' +
    allTasks
      .map(
        (t) =>
          `<option value="${t.id}">${escapeHtml(t.name)} (${t.status})</option>`,
      )
      .join('')

  openModal('quickAssignModal')
}

async function quickAssignToTask() {
  const resourceType = document.getElementById('quickAssignResourceType').value
  const resourceId = document.getElementById('quickAssignResourceId').value
  const taskId = document.getElementById('quickAssignTaskSelect').value

  if (!taskId) {
    showToast('Error', 'Please select a task', 'error')
    return
  }

  const typeMap = {
    proxy: 'proxies',
    card: 'cards',
    email: 'emails',
    account: 'accounts',
  }

  try {
    await apiRequest(
      `/api/resources/${typeMap[resourceType]}/${resourceId}/assign/${taskId}`,
      { method: 'POST' },
    )
    showToast('Success', 'Resource assigned to task', 'success')
    closeModal('quickAssignModal')
    refreshResourceTab()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to assign resource', 'error')
  }
}

async function releaseResource(resourceTypePlural, resourceId) {
  try {
    await apiRequest(
      `/api/resources/${resourceTypePlural}/${resourceId}/release`,
      { method: 'POST' },
    )
    showToast('Success', 'Resource released', 'success')
    refreshResourceTab()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to release resource', 'error')
  }
}

async function loadCards() {
  try {
    const statusFilter = document.getElementById('cardStatusFilter')?.value
    let url = '/api/resources/cards/'
    if (statusFilter) {
      url += `?status=${statusFilter}`
    }
    const cards = await apiRequest(url)
    allResources.cards = cards
    renderCards(cards)
  } catch (error) {
    console.error('Error loading cards:', error)
  }
}

function renderCards(cards) {
  const container = document.getElementById('cardsList')

  if (cards.length === 0) {
    container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-credit-card"></i>
                </div>
                <h3>No cards yet</h3>
                <p>Add your first card to get started</p>
                <button class="btn btn-primary" onclick="showCardModal()">
                    <i class="fas fa-plus"></i> Add Card
                </button>
            </div>
        `
    return
  }

  container.innerHTML = cards
    .map(
      (card) => `
        <div class="card-item ${card.card_type}">
            <div class="card-header">
                <span class="card-type">${card.card_type}</span>
                <span class="status-badge ${card.status}">${card.status}</span>
            </div>
            <div class="card-number">**** **** **** ${card.last_four || '****'}</div>
            <div class="card-details">
                <div class="card-detail-group">
                    <span class="card-detail-label">Cardholder</span>
                    <span class="card-detail-value">${escapeHtml(card.holder_name || 'N/A')}</span>
                </div>
                <div class="card-detail-group">
                    <span class="card-detail-label">Expires</span>
                    <span class="card-detail-value">${card.expiry_month || 'MM'}/${card.expiry_year || 'YY'}</span>
                </div>
                ${card.assigned_task_id ? `<div class="card-detail-group"><span class="card-detail-label">Assigned</span><span class="card-detail-value">Task ${card.assigned_task_id.slice(0, 8)}</span></div>` : ''}
            </div>
            <div class="card-actions">
                <button class="btn btn-sm btn-ghost" onclick="showCardModal('${card.id}')" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                ${
                  card.assigned_task_id
                    ? `<button class="btn btn-sm btn-warning" onclick="releaseResource('cards', '${card.id}')" title="Release"><i class="fas fa-unlink"></i></button>`
                    : `<button class="btn btn-sm btn-ghost" onclick="showAssignModal('card', '${card.id}')" title="Assign to Task"><i class="fas fa-link"></i></button>`
                }
                <button class="btn btn-sm btn-ghost" onclick="deleteCard('${card.id}')" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `,
    )
    .join('')
}

function showCardModal(cardId = null) {
  document.getElementById('cardForm').reset()
  document.getElementById('cardModalTitle').textContent = cardId
    ? 'Edit Card'
    : 'Add New Card'

  // Store card ID for edit mode
  document.getElementById('cardForm').dataset.editId = cardId || ''

  if (cardId && allResources.cards) {
    const card = allResources.cards.find((c) => c.id === cardId)
    if (card) {
      document.getElementById('cardType').value = card.card_type || 'visa'
      document.getElementById('cardNumber').value = card.number || ''
      document.getElementById('cardHolder').value = card.holder_name || ''
      document.getElementById('cardExpMonth').value = card.expiry_month || ''
      document.getElementById('cardExpYear').value = card.expiry_year || ''
      document.getElementById('cardCvv').value = card.cvv || ''
    }
  }

  openModal('cardModal')
}

async function saveCard() {
  const editId = document.getElementById('cardForm').dataset.editId
  const isEdit = !!editId

  const data = {
    card_type: document.getElementById('cardType').value,
    number: document.getElementById('cardNumber').value.replace(/\s/g, ''),
    holder_name: document.getElementById('cardHolder').value.trim(),
    expiry_month: parseInt(document.getElementById('cardExpMonth').value),
    expiry_year: parseInt(document.getElementById('cardExpYear').value),
    cvv: document.getElementById('cardCvv').value.trim(),
  }

  if (
    !data.number ||
    !data.holder_name ||
    !data.expiry_month ||
    !data.expiry_year ||
    !data.cvv
  ) {
    showToast('Error', 'All fields are required', 'error')
    return
  }

  try {
    if (isEdit) {
      await apiRequest(`/api/resources/cards/${editId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Card updated', 'success')
    } else {
      await apiRequest('/api/resources/cards/', {
        method: 'POST',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Card added', 'success')
    }
    closeModal('cardModal')
    loadCards()
    loadDashboardData()
  } catch (error) {
    showToast('Error', `Failed to ${isEdit ? 'update' : 'add'} card`, 'error')
  }
}

async function deleteCard(cardId) {
  if (!confirm('Delete this card?')) return

  try {
    await apiRequest(`/api/resources/cards/${cardId}`, { method: 'DELETE' })
    showToast('Success', 'Card deleted', 'success')
    loadCards()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to delete card', 'error')
  }
}

async function loadEmails() {
  try {
    const statusFilter = document.getElementById('emailStatusFilter')?.value
    let url = '/api/resources/emails/'
    if (statusFilter) {
      url += `?status=${statusFilter}`
    }
    const emails = await apiRequest(url)
    allResources.emails = emails
    renderEmails(emails)
  } catch (error) {
    console.error('Error loading emails:', error)
  }
}

function renderEmails(emails) {
  const tbody = document.getElementById('emailsTableBody')

  if (emails.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 3rem; color: var(--gray-500);">
                    No emails found. Add your first email.
                </td>
            </tr>
        `
    return
  }

  tbody.innerHTML = emails
    .map(
      (email) => `
        <tr>
            <td><strong>${escapeHtml(email.address)}</strong></td>
            <td>${email.provider || 'Unknown'}</td>
            <td><span class="status-badge ${email.status}">${email.status}</span></td>
            <td>${email.verified ? '<i class="fas fa-check-circle" style="color: var(--accent-green);"></i>' : '<i class="fas fa-times-circle" style="color: var(--gray-400);"></i>'}</td>
            <td>${email.assigned_task_id ? 'Task ' + email.assigned_task_id.slice(0, 8) : '-'}</td>
            <td>
                <div class="task-actions">
                    <button class="btn btn-sm btn-ghost" onclick="showEmailModal('${email.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${
                      email.assigned_task_id
                        ? `<button class="btn btn-sm btn-warning" onclick="releaseResource('emails', '${email.id}')" title="Release"><i class="fas fa-unlink"></i></button>`
                        : `<button class="btn btn-sm btn-ghost" onclick="showAssignModal('email', '${email.id}')" title="Assign"><i class="fas fa-link"></i></button>`
                    }
                    <button class="btn btn-sm btn-ghost" onclick="deleteEmail('${email.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `,
    )
    .join('')
}

function showEmailModal(emailId = null) {
  document.getElementById('emailForm').reset()
  document.getElementById('emailModalTitle').textContent = emailId
    ? 'Edit Email'
    : 'Add New Email'
  document.getElementById('emailForm').dataset.editId = emailId || ''

  if (emailId && allResources.emails) {
    const email = allResources.emails.find((e) => e.id === emailId)
    if (email) {
      document.getElementById('emailAddress').value = email.address || ''
      document.getElementById('emailProvider').value = email.provider || 'gmail'
      document.getElementById('emailPassword').value = email.password || ''
    }
  }

  openModal('emailModal')
}

async function saveEmail() {
  const editId = document.getElementById('emailForm').dataset.editId
  const isEdit = !!editId

  const data = {
    address: document.getElementById('emailAddress').value.trim(),
    provider: document.getElementById('emailProvider').value,
    password: document.getElementById('emailPassword').value,
  }

  if (!data.address || !data.password) {
    showToast('Error', 'Email and password are required', 'error')
    return
  }

  try {
    if (isEdit) {
      await apiRequest(`/api/resources/emails/${editId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Email updated', 'success')
    } else {
      await apiRequest('/api/resources/emails/', {
        method: 'POST',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Email added', 'success')
    }
    closeModal('emailModal')
    loadEmails()
    loadDashboardData()
  } catch (error) {
    showToast('Error', `Failed to ${isEdit ? 'update' : 'add'} email`, 'error')
  }
}

async function deleteEmail(emailId) {
  if (!confirm('Delete this email?')) return

  try {
    await apiRequest(`/api/resources/emails/${emailId}`, { method: 'DELETE' })
    showToast('Success', 'Email deleted', 'success')
    loadEmails()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to delete email', 'error')
  }
}

async function loadAccounts() {
  try {
    const statusFilter = document.getElementById('accountStatusFilter')?.value
    let url = '/api/resources/accounts/'
    if (statusFilter) {
      url += `?status=${statusFilter}`
    }
    const accounts = await apiRequest(url)
    allResources.accounts = accounts
    renderAccounts(accounts)
  } catch (error) {
    console.error('Error loading accounts:', error)
  }
}

function renderAccounts(accounts) {
  const tbody = document.getElementById('accountsTableBody')

  if (accounts.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 3rem; color: var(--gray-500);">
                    No accounts found. Add your first account.
                </td>
            </tr>
        `
    return
  }

  tbody.innerHTML = accounts
    .map(
      (account) => `
        <tr>
            <td><strong>${escapeHtml(account.platform)}</strong></td>
            <td>${escapeHtml(account.username)}</td>
            <td><span class="status-badge">${account.platform_type || 'generic'}</span></td>
            <td><span class="status-badge ${account.status}">${account.status}</span></td>
            <td>${account.two_factor_enabled ? '<i class="fas fa-shield-alt" style="color: var(--accent-green);"></i>' : '<i class="fas fa-shield-alt" style="color: var(--gray-400);"></i>'}</td>
            <td>${account.assigned_task_id ? 'Task ' + account.assigned_task_id.slice(0, 8) : '-'}</td>
            <td>
                <div class="task-actions">
                    <button class="btn btn-sm btn-ghost" onclick="showAccountModal('${account.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${
                      account.assigned_task_id
                        ? `<button class="btn btn-sm btn-warning" onclick="releaseResource('accounts', '${account.id}')" title="Release"><i class="fas fa-unlink"></i></button>`
                        : `<button class="btn btn-sm btn-ghost" onclick="showAssignModal('account', '${account.id}')" title="Assign"><i class="fas fa-link"></i></button>`
                    }
                    <button class="btn btn-sm btn-ghost" onclick="deleteAccount('${account.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `,
    )
    .join('')
}

function showAccountModal(accountId = null) {
  document.getElementById('accountForm').reset()
  document.getElementById('accountModalTitle').textContent = accountId
    ? 'Edit Account'
    : 'Add New Account'
  document.getElementById('accountForm').dataset.editId = accountId || ''

  if (accountId && allResources.accounts) {
    const account = allResources.accounts.find((a) => a.id === accountId)
    if (account) {
      document.getElementById('accountPlatform').value = account.platform || ''
      document.getElementById('accountType').value =
        account.platform_type || 'social'
      document.getElementById('accountUsername').value = account.username || ''
      document.getElementById('accountPassword').value = account.password || ''
    }
  }

  openModal('accountModal')
}

async function saveAccount() {
  const editId = document.getElementById('accountForm').dataset.editId
  const isEdit = !!editId

  const data = {
    platform: document.getElementById('accountPlatform').value.trim(),
    platform_type: document.getElementById('accountType').value,
    username: document.getElementById('accountUsername').value.trim(),
    password: document.getElementById('accountPassword').value,
  }

  if (!data.platform || !data.username || !data.password) {
    showToast('Error', 'Platform, username, and password are required', 'error')
    return
  }

  try {
    if (isEdit) {
      await apiRequest(`/api/resources/accounts/${editId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Account updated', 'success')
    } else {
      await apiRequest('/api/resources/accounts/', {
        method: 'POST',
        body: JSON.stringify(data),
      })
      showToast('Success', 'Account added', 'success')
    }
    closeModal('accountModal')
    loadAccounts()
    loadDashboardData()
  } catch (error) {
    showToast(
      'Error',
      `Failed to ${isEdit ? 'update' : 'add'} account`,
      'error',
    )
  }
}

async function deleteAccount(accountId) {
  if (!confirm('Delete this account?')) return

  try {
    await apiRequest(`/api/resources/accounts/${accountId}`, {
      method: 'DELETE',
    })
    showToast('Success', 'Account deleted', 'success')
    loadAccounts()
    loadDashboardData()
  } catch (error) {
    showToast('Error', 'Failed to delete account', 'error')
  }
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/api/monitor/ws`

  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    updateConnectionStatus(true)
    addLogEntry('Connected to monitoring server', 'success')
    checkHealthStatus()
  }

  ws.onclose = () => {
    updateConnectionStatus(false)
    addLogEntry('Disconnected from server', 'warning')

    // Reconnect after 5 seconds
    setTimeout(connectWebSocket, 5000)
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    addLogEntry('Connection error', 'error')
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e)
    }
  }
}

async function checkHealthStatus() {
  try {
    const health = await apiRequest('/api/monitor/health')
    const apiDot = document.querySelector(
      '.status-items .status-row:first-child .status-dot',
    )
    const apiBadge = document.querySelector(
      '.status-items .status-row:first-child .status-badge',
    )

    if (apiDot) apiDot.className = 'status-dot green'
    if (apiBadge) {
      apiBadge.className = 'status-badge green'
      apiBadge.textContent = 'Online'
    }

    addLogEntry(`Health check: ${health.status}`, 'success')
  } catch (error) {
    addLogEntry('Health check failed', 'error')
  }
}

// Check health periodically
setInterval(checkHealthStatus, 60000)

function updateConnectionStatus(connected) {
  const badge = document.getElementById('connectionBadge')
  const mobileBadge = document.getElementById('mobileConnectionBadge')
  const wsStatusDot = document.getElementById('wsStatusDot')
  const wsStatusBadge = document.getElementById('wsStatusBadge')

  // Update both desktop and mobile badges
  ;[badge, mobileBadge].forEach((b) => {
    if (b) {
      if (connected) {
        b.classList.add('connected')
        b.querySelector('.text').textContent = 'Live'
      } else {
        b.classList.remove('connected')
        b.querySelector('.text').textContent = 'Reconnecting...'
      }
    }
  })

  if (wsStatusDot) {
    wsStatusDot.className = 'status-dot ' + (connected ? 'green' : 'yellow')
  }

  if (wsStatusBadge) {
    wsStatusBadge.className = 'status-badge ' + (connected ? 'green' : 'yellow')
    wsStatusBadge.textContent = connected ? 'Connected' : 'Reconnecting'
  }
}

function handleWebSocketMessage(data) {
  switch (data.type) {
    case 'task_update':
      addLogEntry(`Task "${data.task?.name}": ${data.task?.status}`, 'info')
      loadDashboardData()
      if (currentView === 'tasks') loadTasks()
      break
    case 'task_stage':
      addLogEntry(`Task "${data.task_id}" stage: ${data.stage}`, 'info')
      break
    case 'task_error':
      addLogEntry(`Error in task "${data.task_id}": ${data.error}`, 'error')
      loadDashboardData()
      break
    case 'resource_update':
      addLogEntry(`Resource updated: ${data.resource_type}`, 'info')
      loadDashboardData()
      if (currentView === 'resources') refreshResourceTab()
      break
    default:
      addLogEntry(JSON.stringify(data), 'info')
  }
}

function addLogEntry(message, type = 'info') {
  if (isPaused) return

  const log = document.getElementById('activityLog')
  if (!log) return

  const entry = document.createElement('div')
  entry.className = `log-item ${type}`
  entry.innerHTML = `
        <span class="log-time">${getTimeString()}</span>
        <span class="log-text">${escapeHtml(message)}</span>
    `

  log.appendChild(entry)

  // Keep only last 100 entries
  while (log.children.length > 100) {
    log.removeChild(log.firstChild)
  }

  // Auto-scroll to bottom
  log.scrollTop = log.scrollHeight
}

function showToast(title, message, type = 'info') {
  const container = document.getElementById('toastContainer')
  if (!container) return

  const icons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle',
  }

  const toast = document.createElement('div')
  toast.className = `toast ${type}`
  toast.innerHTML = `
        <i class="fas ${icons[type]} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${escapeHtml(title)}</div>
            <div class="toast-message">${escapeHtml(message)}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `

  container.appendChild(toast)

  // Auto-remove after 5 seconds
  setTimeout(() => {
    toast.style.opacity = '0'
    toast.style.transform = 'translateX(100%)'
    setTimeout(() => toast.remove(), 300)
  }, 5000)
}

function escapeHtml(text) {
  if (!text) return ''
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

function getTimeString() {
  return new Date().toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}
