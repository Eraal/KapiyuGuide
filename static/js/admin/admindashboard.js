// dashboard.js - Dashboard-specific functionality
console.log("Initializing Dashboard Manager");

class DashboardManager {
    constructor(socketManager) {
        this.socketManager = socketManager;
        this.charts = {};
        this.chartData = {
            weekly: {
                labels: [],
                newInquiries: [],
                resolved: []
            },
            monthly: {
                labels: [],
                newInquiries: [],
                resolved: []
            }
        };
    }

    initialize() {
        // Initialize the dashboard UI
        this._initializeDashboardUI();
        
        this._initializeCharts();
        
        this._setupChartControls();
        
        this._setupLiveUpdates();
    }

    _initializeDashboardUI() {
        // Display current date
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const currentDateElement = document.getElementById('current-date');
        if (currentDateElement) {
            currentDateElement.textContent = now.toLocaleDateString('en-PH', options);
        }
    }

    _initializeCharts() {
        // Ensure we have default data for charts
        const defaultWeekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const defaultMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        // Get chart data with better error handling and fallbacks
        this.chartData.weekly.labels = this._getJsonData('weekly-labels-data', defaultWeekDays);
        this.chartData.weekly.newInquiries = this._getJsonData('weekly-new-inquiries-data', [0, 1, 0, 2, 0, 1, 0]);
        this.chartData.weekly.resolved = this._getJsonData('weekly-resolved-data', [0, 0, 0, 1, 0, 1, 0]);
        
        this.chartData.monthly.labels = this._getJsonData('monthly-labels-data', defaultMonths);
        this.chartData.monthly.newInquiries = this._getJsonData('monthly-new-inquiries-data', [1, 2, 0, 1, 3, 2, 0, 1, 0, 2, 1, 0]);
        this.chartData.monthly.resolved = this._getJsonData('monthly-resolved-data', [0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 1, 0]);

        // Initialize Pie Chart
        this._initializePieChart();
        
        // Initialize Line Chart
        this._initializeLineChart();
        
        // Add active class to the default chart period button
        const defaultChartButton = document.querySelector('[data-chart="weekly"]');
        if (defaultChartButton) {
            defaultChartButton.classList.add('active-chart', 'bg-red-50', 'text-red-700', 'border-red-700');
        }
    }
    
    _initializePieChart() {
        const pieCtx = document.getElementById('inquiriesPieChart');
        if (!pieCtx) return;
        
        const pendingCount = this._getPendingCount();
        const resolvedCount = this._getResolvedCount();
        const totalCount = this._getTotalCount();

        // If all values are 0, set at least one value to 1 to show the chart
        let pieData = [pendingCount, resolvedCount, 0]; // Third value is "in progress"
        if (pendingCount === 0 && resolvedCount === 0 && totalCount === 0) {
            pieData = [1, 0, 0]; // Show at least one pending to make chart visible
        }

        this.charts.pieChart = new Chart(pieCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Resolved', 'In Progress'],
                datasets: [{
                    data: pieData,
                    backgroundColor: ['#fbbf24', '#10b981', '#3b82f6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            boxWidth: 12,
                            font: {
                                family: "'Inter', sans-serif"
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Inquiries by Status',
                        font: {
                            size: 16,
                            weight: 'bold',
                            family: "'Inter', sans-serif"
                        }
                    }
                },
                cutout: '70%',
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }
    
    _initializeLineChart() {
        const lineCtx = document.getElementById('inquiriesTrendChart');
        if (!lineCtx) return;

        this.charts.trendChart = new Chart(lineCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: this.chartData.weekly.labels,
                datasets: [{
                    label: 'New Inquiries',
                    data: this.chartData.weekly.newInquiries,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#ef4444',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }, {
                    label: 'Resolved Inquiries',
                    data: this.chartData.weekly.resolved,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            boxWidth: 12,
                            font: {
                                family: "'Inter', sans-serif"
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Weekly Inquiries Trend',
                        font: {
                            size: 16,
                            weight: 'bold',
                            family: "'Inter', sans-serif"
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                family: "'Inter', sans-serif"
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                family: "'Inter', sans-serif"
                            }
                        }
                    }
                },
                animations: {
                    radius: {
                        duration: 400,
                        easing: 'linear'
                    }
                }
            }
        });
    }

    _setupChartControls() {
        const chartButtons = document.querySelectorAll('[data-chart]');
        chartButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons
                chartButtons.forEach(btn => {
                    btn.classList.remove('active-chart', 'bg-red-50', 'text-red-700', 'border-red-700');
                });

                // Add active class to clicked button
                button.classList.add('active-chart', 'bg-red-50', 'text-red-700', 'border-red-700');

                // Update chart data based on selected period
                const period = button.getAttribute('data-chart');
                this._updateTrendChart(period);
            });
        });
    }

    _updateTrendChart(period) {
        if (!this.charts.trendChart) return;
        
        if (period === 'weekly') {
            this.charts.trendChart.data.labels = this.chartData.weekly.labels;
            this.charts.trendChart.data.datasets[0].data = this.chartData.weekly.newInquiries;
            this.charts.trendChart.data.datasets[1].data = this.chartData.weekly.resolved;
            this.charts.trendChart.options.plugins.title.text = 'Weekly Inquiries Trend';
        } else if (period === 'monthly') {
            this.charts.trendChart.data.labels = this.chartData.monthly.labels;
            this.charts.trendChart.data.datasets[0].data = this.chartData.monthly.newInquiries;
            this.charts.trendChart.data.datasets[1].data = this.chartData.monthly.resolved;
            this.charts.trendChart.options.plugins.title.text = 'Monthly Inquiries Trend';
        }

        this.charts.trendChart.update();
    }

    _setupLiveUpdates() {
        if (!this.socketManager) {
            console.error('Socket manager not available for live updates');
            return;
        }

        // Listen for new inquiry notifications
        this.socketManager.on('new_inquiry', (data) => {
            try {
                console.log('New inquiry received:', data);

                // Update counter elements
                this._incrementCounter('pending-inquiries-count');
                this._incrementCounter('total-inquiries-count');

                // Update recent activities
                this._addRecentActivity({
                    action: `submitted a new inquiry to ${data.office || 'an office'}`,
                    actor: {
                        role: 'student',
                        first_name: data.student_name.split(' ')[0] || '',
                        last_name: data.student_name.split(' ')[1] || ''
                    },
                    timestamp: new Date()
                });

                // Update charts
                this._updatePieChart();
                this._updateTrendChartWithNewInquiry();

                // Play notification sound if available
                this._playNotificationSound();

            } catch (error) {
                console.error('Error handling new_inquiry event:', error);
            }
        });

        // Listen for resolved inquiry notifications
        this.socketManager.on('resolved_inquiry', (data) => {
            console.log('Resolved inquiry received:', data);

            // Update counter elements
            this._incrementCounter('resolved-inquiries-count');
            this._decrementCounter('pending-inquiries-count');

            // Add to recent activities
            this._addRecentActivity({
                action: `resolved an inquiry`,
                actor: {
                    role: 'office_admin',
                    first_name: data.admin_name.split(' ')[0] || '',
                    last_name: data.admin_name.split(' ')[1] || ''
                },
                timestamp: new Date()
            });

            // Update charts
            this._updatePieChart();
            this._updateTrendChartWithResolvedInquiry();
        });

        // Listen for new counseling session notifications
        this.socketManager.on('new_session', (data) => {
            console.log('New counseling session:', data);

            // Add to upcoming sessions
            this._addCounselingSession({
                student: {
                    user: {
                        first_name: data.student_name.split(' ')[0] || '',
                        last_name: data.student_name.split(' ')[1] || '',
                        get_full_name: function() { return data.student_name; }
                    }
                },
                office: { name: data.office_name },
                scheduled_at: new Date(data.scheduled_at),
                status: data.status || 'scheduled'
            });

            // Add to recent activities
            this._addRecentActivity({
                action: `scheduled a counseling session with ${data.office_name}`,
                actor: {
                    role: 'student',
                    first_name: data.student_name.split(' ')[0] || '',
                    last_name: data.student_name.split(' ')[1] || ''
                },
                timestamp: new Date()
            });
        });

        // Listen for system log notifications
        this.socketManager.on('system_log', (data) => {
            console.log('System log received:', data);

            // Add to system logs
            this._addSystemLog({
                action: data.action,
                actor: data.actor,
                timestamp: new Date(),
                is_success: data.is_success
            });
        });
    }

    _updatePieChart() {
        if (!this.charts.pieChart) return;

        const pendingCount = this._getPendingCount();
        const resolvedCount = this._getResolvedCount();
        const totalCount = this._getTotalCount();
        const inProgressCount = Math.max(0, totalCount - pendingCount - resolvedCount);

        this.charts.pieChart.data.datasets[0].data = [pendingCount, resolvedCount, inProgressCount];
        this.charts.pieChart.update();
    }

    _updateTrendChartWithNewInquiry() {
        if (!this.charts.trendChart) return;
        
        const today = new Date().getDay();
        
        // Update weekly data
        if (this.chartData.weekly.newInquiries[today] !== undefined) {
            this.chartData.weekly.newInquiries[today] += 1;
        }
        
        // Update monthly data
        const currentMonth = new Date().getMonth();
        if (this.chartData.monthly.newInquiries[currentMonth] !== undefined) {
            this.chartData.monthly.newInquiries[currentMonth] += 1;
        }
        
        // Update the visible chart if needed
        const activeChartButton = document.querySelector('[data-chart].active-chart');
        if (activeChartButton) {
            this._updateTrendChart(activeChartButton.getAttribute('data-chart'));
        }
    }

    _updateTrendChartWithResolvedInquiry() {
        if (!this.charts.trendChart) return;
        
        const today = new Date().getDay();
        
        // Update weekly data
        if (this.chartData.weekly.resolved[today] !== undefined) {
            this.chartData.weekly.resolved[today] += 1;
        }
        
        // Update monthly data
        const currentMonth = new Date().getMonth();
        if (this.chartData.monthly.resolved[currentMonth] !== undefined) {
            this.chartData.monthly.resolved[currentMonth] += 1;
        }
        
        // Update the visible chart if needed
        const activeChartButton = document.querySelector('[data-chart].active-chart');
        if (activeChartButton) {
            this._updateTrendChart(activeChartButton.getAttribute('data-chart'));
        }
    }

    // Updated to match the HTML structure
    _addRecentActivity(activity) {
        const activitiesContainer = document.getElementById('recent-activities');
        if (!activitiesContainer) return;

        const activityClass = this._getActivityClass(activity.action);
        
        const now = new Date();
        const formattedTime = now.toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            hour: 'numeric', 
            minute: 'numeric', 
            hour12: true 
        });

        const activityHtml = `
            <div class="${activityClass} pl-3 py-2 transition-all duration-300 rounded-r-lg">
                <p class="text-sm font-medium text-gray-800">
                    ${activity.actor ? `${this._formatActorRole(activity.actor)} ${activity.actor.first_name} ${activity.actor.last_name}` : 'System'} ${activity.action}
                </p>
                <p class="text-xs text-gray-500">
                    ${formattedTime}
                </p>
            </div>
        `;

        // Add to the top of the list
        activitiesContainer.insertAdjacentHTML('afterbegin', activityHtml);

        // Remove old entries if too many
        const activities = activitiesContainer.querySelectorAll('div');
        if (activities.length > 10) {
            activities[activities.length - 1].remove();
        }
    }
    
    // Updated to match the HTML structure
    _addCounselingSession(session) {
        const sessionsContainer = document.getElementById('upcoming-sessions');
        if (!sessionsContainer) return;

        const formattedDate = session.scheduled_at.toLocaleString('en-US', { 
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true 
        });

        const statusClass = this._getStatusClass(session.status);

        const sessionHtml = `
            <div class="p-4 flex items-center justify-between transition-all duration-300 hover:bg-gray-50">
                <div>
                    <p class="font-medium">
                        ${session.student.user.get_full_name()} with ${session.office.name}
                    </p>
                    <p class="text-sm text-gray-500">
                        ${formattedDate}
                    </p>
                </div>
                <span class="px-2 py-1 ${statusClass} text-xs rounded-full">
                    ${session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                </span>
            </div>
        `;

        // Add to the container
        sessionsContainer.insertAdjacentHTML('afterbegin', sessionHtml);

        // Remove old entries if too many
        const sessions = sessionsContainer.querySelectorAll('div[class^="p-4 flex items-center"]');
        if (sessions.length > 3) {
            sessions[sessions.length - 1].remove();
        }
    }
    
    // Updated to match the HTML structure
    _addSystemLog(log) {
        const logsContainer = document.getElementById('system-logs');
        if (!logsContainer) return;

        const statusClass = log.is_success ? 'bg-green-500' : 'bg-red-500';
        const formattedTime = new Date(log.timestamp).toLocaleString('en-US', { 
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true 
        });

        const logHtml = `
            <div class="text-sm border-l-2 border-gray-300 pl-3 py-1 transition-all duration-300 hover:bg-gray-50 rounded-r-lg">
                <p class="font-medium flex items-center">
                    <span class="h-2 w-2 rounded-full ${statusClass} mr-2"></span>
                    ${log.action} ${log.actor ? `(${log.actor.role})` : ''}
                </p>
                <p class="text-xs text-gray-500">
                    ${formattedTime}
                </p>
            </div>
        `;

        // Add to the top of the list
        logsContainer.insertAdjacentHTML('afterbegin', logHtml);

        // Remove old entries if too many
        const logs = logsContainer.querySelectorAll('div[class^="text-sm border-l-2"]');
        if (logs.length > 5) {
            logs[logs.length - 1].remove();
        }
    }

    // Helper methods
    _getActivityClass(action) {
        let baseClass = 'border-l-4 pl-3 py-2 transition-all duration-300 rounded-r-lg';
        
        if (action.toLowerCase().includes('new')) {
            return `${baseClass} border-blue-500 hover:bg-blue-50`;
        } else if (action.toLowerCase().includes('resolved')) {
            return `${baseClass} border-green-500 hover:bg-green-50`;
        } else if (action.toLowerCase().includes('inquiry')) {
            return `${baseClass} border-yellow-500 hover:bg-yellow-50`;
        } else if (action.toLowerCase().includes('login')) {
            return `${baseClass} border-purple-500 hover:bg-purple-50`;
        } else if (action.toLowerCase().includes('logout')) {
            return `${baseClass} border-indigo-500 hover:bg-indigo-50`;
        } else {
            return `${baseClass} border-red-500 hover:bg-red-50`;
        }
    }

    _getStatusClass(status) {
        if (status === 'scheduled') {
            return 'bg-blue-100 text-blue-800';
        } else if (status === 'confirmed') {
            return 'bg-green-100 text-green-800';
        } else if (status === 'waiting') {
            return 'bg-yellow-100 text-yellow-800';
        } else {
            return 'bg-gray-100 text-gray-800';
        }
    }

    _formatActorRole(actor) {
        if (actor.role === 'super_admin') {
            return 'Super Admin';
        } else if (actor.role === 'office_admin') {
            return 'Office Admin';
        } else if (actor.role === 'student') {
            return 'Student';
        } else {
            return actor.role || '';
        }
    }

    _playNotificationSound() {
        const notificationSound = document.getElementById('notification-sound');
        if (notificationSound) {
            notificationSound.play().catch(e => console.warn('Could not play notification sound', e));
        }
    }

    _incrementCounter(elementId) {
        const counterElement = document.getElementById(elementId);
        if (counterElement) {
            const currentValue = parseInt(counterElement.textContent, 10) || 0;
            counterElement.textContent = currentValue + 1;
        }
    }

    _decrementCounter(elementId) {
        const counterElement = document.getElementById(elementId);
        if (counterElement) {
            const currentValue = parseInt(counterElement.textContent, 10) || 0;
            if (currentValue > 0) {
                counterElement.textContent = currentValue - 1;
            }
        }
    }

    _getPendingCount() {
        const pendingCountElement = document.getElementById('pending-inquiries-count');
        return pendingCountElement ? (parseInt(pendingCountElement.textContent, 10) || 0) : 0;
    }

    _getResolvedCount() {
        const resolvedCountElement = document.getElementById('resolved-inquiries-count');
        return resolvedCountElement ? (parseInt(resolvedCountElement.textContent, 10) || 0) : 0;
    }

    _getTotalCount() {
        const totalCountElement = document.getElementById('total-inquiries-count');
        return totalCountElement ? (parseInt(totalCountElement.textContent, 10) || 0) : 0;
    }

    _getJsonData(elementId, defaultValue = []) {
        try {
            const element = document.getElementById(elementId);
            if (!element) return defaultValue;
            
            const data = JSON.parse(element.textContent);
            return Array.isArray(data) ? data : defaultValue;
        } catch (e) {
            console.error(`Error parsing data from element ${elementId}:`, e);
            return defaultValue;
        }
    }
}

if (document.readyState === 'complete' || document.readyState === 'interactive') {
   
    const socketManager = window.socketManager || null;
    const dashboardManager = new DashboardManager(socketManager);
    window.dashboardManager = dashboardManager;
    dashboardManager.initialize();
    
    console.log('Dashboard initialized');
} else {
    // Wait for the DOM to be fully loaded
    document.addEventListener('DOMContentLoaded', () => {
        const socketManager = window.socketManager || null;     
        const dashboardManager = new DashboardManager(socketManager);
        window.dashboardManager = dashboardManager;
        dashboardManager.initialize();
        
        console.log('Dashboard initialized on DOMContentLoaded');
    });
}