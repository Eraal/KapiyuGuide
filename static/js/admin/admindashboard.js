document.addEventListener('DOMContentLoaded', function () {
    // Initialize the dashboard immediately to show UI elements
    initializeDashboard();

    if (typeof io === 'undefined') {
        console.log('Loading Socket.IO library...');
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.1/socket.io.min.js';
        script.onload = function () {
            console.log('Socket.IO loaded successfully');
            initializeSocketIO();
        };
        script.onerror = function () {
            console.error('Failed to load Socket.IO');
            showNotification('Connection Error', 'Failed to establish real-time connection.', 'error');
        };
        document.head.appendChild(script);
    } else {
        console.log('Socket.IO already loaded');
        initializeSocketIO();
    }

    function initializeSocketIO() {
        try {
            // Initialize Socket.IO connection with more comprehensive options
            window.socket = io.connect(window.location.origin, {
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: Infinity,
                timeout: 20000,
                autoConnect: true
            });

            // Enhanced connection events with better logging
            socket.on('connect', function () {
                console.log('Connected to WebSocket server with ID:', socket.id);
                const statusIndicator = document.getElementById('connection-status');
                if (statusIndicator) {
                    statusIndicator.classList.remove('bg-red-500');
                    statusIndicator.classList.add('bg-green-500');
                    statusIndicator.setAttribute('title', 'Connected to real-time updates');
                }

                // Explicitly join the admin room
                socket.emit('join_admin_room');

                // Add ping to verify connection health
                socket.emit('ping_server', { timestamp: new Date().toISOString() });
            });

            socket.on('connect_error', function (error) {
                console.error('Connection error:', error);
                showNotification('Connection Error', 'Failed to connect. Will retry...', 'error');
            });

            socket.on('connect_timeout', function () {
                console.error('Connection timeout');
                showNotification('Connection Timeout', 'Connection timed out. Will retry...', 'warning');
            });

            socket.on('disconnect', function (reason) {
                console.log('Disconnected from WebSocket server. Reason:', reason);
                const statusIndicator = document.getElementById('connection-status');
                if (statusIndicator) {
                    statusIndicator.classList.remove('bg-green-500');
                    statusIndicator.classList.add('bg-red-500');
                    statusIndicator.setAttribute('title', 'Disconnected from real-time updates');
                }

                // Show a notification only for unexpected disconnects
                if (reason !== 'io client disconnect') {
                    showNotification('Disconnected', 'Real-time updates paused. Reconnecting...', 'warning');
                }
            });

            // Register event handlers for dashboard updates
            setupLiveUpdates(socket);
        } catch (error) {
            console.error('Error initializing Socket.IO:', error);
            showNotification('WebSocket Error', 'Could not initialize real-time updates', 'error');
        }
    }

    function initializeDashboard() {
        // Display current date
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const currentDateElement = document.getElementById('current-date');
        if (currentDateElement) {
            currentDateElement.textContent = now.toLocaleDateString('en-US', options);
        }

        // Initialize dashboard charts
        initializeCharts();

        // Add active class to the default chart period button
        const defaultChartButton = document.querySelector('[data-chart="weekly"]');
        if (defaultChartButton) {
            defaultChartButton.classList.add('active-chart', 'bg-red-50', 'text-red-700', 'border-red-700');
        }

        // Add hover effects to stat cards
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach(card => {
            card.addEventListener('mouseenter', function () {
                this.classList.add('transform', 'scale-105');
                this.style.transition = 'all 0.3s ease';
            });

            card.addEventListener('mouseleave', function () {
                this.classList.remove('transform', 'scale-105');
            });
        });
    }

    function initializeCharts() {
        // Ensure we have default data for charts
        const defaultWeekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const defaultMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        // Get chart data with better error handling and fallbacks
        const getPendingCount = () => {
            const element = document.getElementById('pending-inquiries-count');
            return element && element.textContent ? parseInt(element.textContent) : 0;
        };

        const getResolvedCount = () => {
            const element = document.getElementById('resolved-inquiries-count');
            return element && element.textContent ? parseInt(element.textContent) : 0;
        };

        const getTotalCount = () => {
            const element = document.getElementById('total-inquiries-count');
            return element && element.textContent ? parseInt(element.textContent) : 0;
        };

        const getJsonData = (elementId, fallback = []) => {
            const element = document.getElementById(elementId);
            if (!element || !element.textContent || element.textContent.trim() === '') {
                return fallback;
            }
            try {
                return JSON.parse(element.textContent);
            } catch (e) {
                console.warn(`Error parsing JSON from ${elementId}:`, e);
                return fallback;
            }
        };

        // Pie Chart - Always render with default data if needed
        const pieCtx = document.getElementById('inquiriesPieChart');
        if (pieCtx) {
            const pendingCount = getPendingCount();
            const resolvedCount = getResolvedCount();
            const totalCount = getTotalCount() || 0;  // Ensure we have at least 0

            // If all values are 0, set at least one value to 1 to show the chart
            let pieData = [pendingCount, resolvedCount, 0]; // Third value is "in progress"
            if (pendingCount === 0 && resolvedCount === 0 && totalCount === 0) {
                pieData = [1, 0, 0]; // Show at least one pending to make chart visible
            }

            const inquiriesPieChart = new Chart(pieCtx.getContext('2d'), {
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

            // Store chart in window object
            window.inquiriesPieChart = inquiriesPieChart;
        }

        // Line Chart - Ensure the line chart always renders with default data if needed
        const lineCtx = document.getElementById('inquiriesTrendChart');
        if (lineCtx) {
            // Default data for the charts with at least some non-zero values
            const defaultWeekData = [0, 1, 0, 2, 0, 1, 0]; // Some sample data so chart is visible
            const defaultMonthData = [1, 2, 0, 1, 3, 2, 0, 1, 0, 2, 1, 0]; // Sample data

            // Get data from the page with guaranteed fallbacks
            const weeklyLabels = getJsonData('weekly-labels-data', defaultWeekDays);
            const weeklyNewInquiries = getJsonData('weekly-new-inquiries-data', defaultWeekData);
            const weeklyResolved = getJsonData('weekly-resolved-data', defaultWeekData.map(v => Math.max(0, v - 1))); // Slightly different
            const monthlyLabels = getJsonData('monthly-labels-data', defaultMonths);
            const monthlyNewInquiries = getJsonData('monthly-new-inquiries-data', defaultMonthData);
            const monthlyResolved = getJsonData('monthly-resolved-data', defaultMonthData.map(v => Math.max(0, v - 1)));

            const inquiriesTrendChart = new Chart(lineCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: weeklyLabels,
                    datasets: [{
                        label: 'New Inquiries',
                        data: weeklyNewInquiries,
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
                        data: weeklyResolved,
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

            // Store chart and data in window object for easy access in WebSocket handlers
            window.inquiriesTrendChart = inquiriesTrendChart;
            window.chartData = {
                weekly: {
                    labels: weeklyLabels,
                    newInquiries: weeklyNewInquiries,
                    resolved: weeklyResolved
                },
                monthly: {
                    labels: monthlyLabels,
                    newInquiries: monthlyNewInquiries,
                    resolved: monthlyResolved
                }
            };

            // Chart toggle functionality
            const chartButtons = document.querySelectorAll('[data-chart]');
            chartButtons.forEach(button => {
                button.addEventListener('click', function () {
                    // Remove active class from all buttons
                    chartButtons.forEach(btn => {
                        btn.classList.remove('active-chart', 'bg-red-50', 'text-red-700', 'border-red-700');
                    });

                    // Add active class to clicked button
                    this.classList.add('active-chart', 'bg-red-50', 'text-red-700', 'border-red-700');

                    // Update chart data based on selected period
                    const period = this.getAttribute('data-chart');

                    if (period === 'weekly') {
                        inquiriesTrendChart.data.labels = window.chartData.weekly.labels;
                        inquiriesTrendChart.data.datasets[0].data = window.chartData.weekly.newInquiries;
                        inquiriesTrendChart.data.datasets[1].data = window.chartData.weekly.resolved;
                        inquiriesTrendChart.options.plugins.title.text = 'Weekly Inquiries Trend';
                    } else if (period === 'monthly') {
                        inquiriesTrendChart.data.labels = window.chartData.monthly.labels;
                        inquiriesTrendChart.data.datasets[0].data = window.chartData.monthly.newInquiries;
                        inquiriesTrendChart.data.datasets[1].data = window.chartData.monthly.resolved;
                        inquiriesTrendChart.options.plugins.title.text = 'Monthly Inquiries Trend';
                    }

                    inquiriesTrendChart.update();
                });
            });
        } else {
            console.warn('Line chart canvas element not found');
        }
    }

    function setupLiveUpdates(socket) {
        // Listen for new inquiry notifications
        if (!socket) {
            console.error('Socket not initialized');
            return;
        }

        // Listen for connection events to verify socket is working
        socket.on('connection_success', function (data) {
            console.log('Connected as:', data.user);
            showNotification('Websocket Connected', 'Real-time updates are now active', 'success');
        });

        socket.on('new_inquiry', function (data) {
            try {
                console.log('New inquiry received:', data);

                const pendingElement = document.querySelector('[data-counter="pending"]');
                if (pendingElement) {
                    const currentCount = parseInt(pendingElement.textContent);
                    pendingElement.textContent = (currentCount + 1).toString();
                }

                // Update the total inquiries count
                const totalElement = document.querySelector('[data-counter="total"]');
                if (totalElement) {
                    const currentTotal = parseInt(totalElement.textContent);
                    totalElement.textContent = (currentTotal + 1).toString();
                }

                // Add to recent activities
                updateRecentActivities({
                    type: 'new_inquiry',
                    student_name: data.student_name,
                    timestamp: data.timestamp || new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true })
                });

                // Play notification sound if available
                const notificationSound = document.getElementById('notification-sound');
                if (notificationSound) {
                    notificationSound.play().catch(e => console.warn('Could not play notification sound', e));
                }

                // Update pie chart
                updatePieChart();

                // Update line chart
                const today = new Date().getDay();
                if (window.inquiriesTrendChart && window.inquiriesTrendChart.data.datasets[0].data[today] !== undefined) {
                    window.inquiriesTrendChart.data.datasets[0].data[today] += 1;
                    window.chartData.weekly.newInquiries[today] += 1;
                    window.inquiriesTrendChart.update();
                }

                // Show notification banner
                showNotification('New inquiry received', `New inquiry from ${data.student_name}`, 'info');

            } catch (error) {
                console.error('Error handling new_inquiry event:', error);
            }
        });

        // Listen for resolved inquiry notifications
        socket.on('resolved_inquiry', function (data) {
            console.log('Resolved inquiry received:', data);

            // Update the resolved inquiries count
            const resolvedElement = document.querySelector('[data-counter="resolved"]');
            if (resolvedElement) {
                const currentCount = parseInt(resolvedElement.textContent);
                resolvedElement.textContent = (currentCount + 1).toString();
            }

            // Update the pending inquiries count
            const pendingElement = document.querySelector('[data-counter="pending"]');
            if (pendingElement) {
                const currentCount = parseInt(pendingElement.textContent);
                pendingElement.textContent = Math.max(0, currentCount - 1).toString();
            }

            // Add to recent activities
            updateRecentActivities({
                type: 'resolved_inquiry',
                admin_name: data.admin_name,
                timestamp: data.timestamp || new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true })
            });

            // Update pie chart
            updatePieChart();

            // Update line chart
            const today = new Date().getDay();
            if (window.inquiriesTrendChart && window.inquiriesTrendChart.data.datasets[1].data[today] !== undefined) {
                window.inquiriesTrendChart.data.datasets[1].data[today] += 1;
                window.chartData.weekly.resolved[today] += 1;
                window.inquiriesTrendChart.update();
            }

            // Show notification banner
            showNotification('Inquiry resolved', `Inquiry resolved by ${data.admin_name}`, 'success');
        });

        // Listen for new counseling session notifications
        socket.on('new_session', function (data) {
            console.log('New counseling session:', data);

            // Add to upcoming sessions
            updateUpcomingSessions({
                student_name: data.student_name,
                office_name: data.office_name,
                scheduled_at: data.scheduled_at,
                status: data.status
            });

            // Add to recent activities
            updateRecentActivities({
                type: 'new_session',
                student_name: data.student_name,
                office_name: data.office_name,
                timestamp: new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true })
            });

            // Show notification banner
            showNotification('New counseling session', `New session scheduled with ${data.student_name}`, 'info');
        });

        // Listen for system log notifications
        socket.on('system_log', function (data) {
            console.log('System log received:', data);

            // Add to system logs
            updateSystemLogs({
                action: data.action,
                actor: data.actor,
                timestamp: data.timestamp
            });

            socket.on('pong_server', function(data) {
                console.log('Server pong received:', data);
            });

            // Show notification banner for important system events
            if (data.action.includes('login') || data.action.includes('created') || !data.is_success) {
                const severity = data.is_success ? 'info' : 'warning';
                showNotification('System event', data.action, severity);
            }
        });
    }

    function updatePieChart() {
        if (!window.inquiriesPieChart) return;

        const pendingElement = document.querySelector('[data-counter="pending"]');
        const resolvedElement = document.querySelector('[data-counter="resolved"]');
        const totalElement = document.querySelector('[data-counter="total"]');

        if (!pendingElement || !resolvedElement || !totalElement) {
            console.warn('Counter elements not found for pie chart update');
            return;
        }

        const pendingCount = parseInt(pendingElement.textContent || 0);
        const resolvedCount = parseInt(resolvedElement.textContent || 0);
        const totalCount = parseInt(totalElement.textContent || 0);
        const inProgressCount = Math.max(0, totalCount - pendingCount - resolvedCount);

        window.inquiriesPieChart.data.datasets[0].data = [pendingCount, resolvedCount, inProgressCount];
        window.inquiriesPieChart.update();
    }

    function updateRecentActivities(activity) {
        const activitiesList = document.getElementById('recent-activities-list');
        if (!activitiesList) return;

        let activityHtml = '';

        if (activity.type === 'new_inquiry') {
            activityHtml = `
                <li class="py-2 border-b border-gray-100 flex items-center">
                    <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                        <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                        </svg>
                    </div>
                    <div class="flex-grow">
                        <p class="text-sm leading-none">
                            <span class="font-medium">${activity.student_name}</span> submitted a new inquiry
                        </p>
                        <p class="text-xs text-gray-500 mt-1">${activity.timestamp}</p>
                    </div>
                </li>
            `;
        } else if (activity.type === 'resolved_inquiry') {
            activityHtml = `
                <li class="py-2 border-b border-gray-100 flex items-center">
                    <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center mr-3">
                        <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                    </div>
                    <div class="flex-grow">
                        <p class="text-sm leading-none">
                            <span class="font-medium">${activity.admin_name}</span> resolved an inquiry
                        </p>
                        <p class="text-xs text-gray-500 mt-1">${activity.timestamp}</p>
                    </div>
                </li>
            `;
        } else if (activity.type === 'new_session') {
            activityHtml = `
                <li class="py-2 border-b border-gray-100 flex items-center">
                    <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                        <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                    <div class="flex-grow">
                        <p class="text-sm leading-none">
                            <span class="font-medium">${activity.student_name}</span> scheduled a session with <span class="font-medium">${activity.office_name}</span>
                        </p>
                        <p class="text-xs text-gray-500 mt-1">${activity.timestamp}</p>
                    </div>
                </li>
            `;
        }

        if (activityHtml) {
            // Add to the top of the list
            activitiesList.insertAdjacentHTML('afterbegin', activityHtml);

            // Remove the last item if more than 5
            const listItems = activitiesList.querySelectorAll('li');
            if (listItems.length > 5) {
                listItems[listItems.length - 1].remove();
            }
        }
    }

    // Helper function to update upcoming sessions list
    function updateUpcomingSessions(session) {
        const sessionsList = document.getElementById('upcoming-sessions-list');
        if (!sessionsList) return;

        const sessionDate = new Date(session.scheduled_at);
        const formattedDate = sessionDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const formattedTime = sessionDate.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });

        const sessionHtml = `
            <li class="py-2 border-b border-gray-100 flex items-center">
                <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
                    <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div class="flex-grow">
                    <p class="text-sm leading-none">
                        <span class="font-medium">${session.student_name}</span> with <span class="font-medium">${session.office_name}</span>
                    </p>
                    <p class="text-xs text-gray-500 mt-1">${formattedDate} at ${formattedTime}</p>
                </div>
                <div class="ml-2">
                    <span class="px-2 py-1 text-xs rounded-full ${session.status === 'scheduled' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'}">
                        ${session.status}
                    </span>
                </div>
            </li>
        `;

        // Add to the list in chronological order
        const listItems = sessionsList.querySelectorAll('li');
        let inserted = false;

        if (listItems.length > 0) {
            for (let i = 0; i < listItems.length; i++) {
                const itemDate = new Date(listItems[i].querySelector('.text-gray-500').textContent);
                if (sessionDate < itemDate) {
                    listItems[i].insertAdjacentHTML('beforebegin', sessionHtml);
                    inserted = true;
                    break;
                }
            }
        }

        if (!inserted) {
            sessionsList.insertAdjacentHTML('beforeend', sessionHtml);
        }

        // Remove the last item if more than 3
        const updatedListItems = sessionsList.querySelectorAll('li');
        if (updatedListItems.length > 3) {
            updatedListItems[updatedListItems.length - 1].remove();
        }
    }

    // Helper function to update system logs
    function updateSystemLogs(log) {
        const logsList = document.getElementById('system-logs-list');
        if (!logsList) return;

        let iconClass = 'text-gray-600 bg-gray-100';
        if (log.action.includes('login')) {
            iconClass = 'text-blue-600 bg-blue-100';
        } else if (log.action.includes('created')) {
            iconClass = 'text-green-600 bg-green-100';
        } else if (!log.is_success) {
            iconClass = 'text-red-600 bg-red-100';
        }

        const logHtml = `
            <li class="py-2 border-b border-gray-100 flex items-center">
                <div class="w-8 h-8 rounded-full ${iconClass.split(' ')[1]} flex items-center justify-center mr-3">
                    <svg class="w-4 h-4 ${iconClass.split(' ')[0]}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div class="flex-grow">
                    <p class="text-sm leading-none">
                        ${log.action}
                    </p>
                    <p class="text-xs text-gray-500 mt-1">
                        <span class="font-medium">${log.actor.name}</span> (${log.actor.role}) - ${log.timestamp}
                    </p>
                </div>
            </li>
        `;

        // Add to the top of the list
        logsList.insertAdjacentHTML('afterbegin', logHtml);

        // Remove the last item if more than 5
        const listItems = logsList.querySelectorAll('li');
        if (listItems.length > 5) {
            listItems[listItems.length - 1].remove();
        }
    }

    function showNotification(title, message, type = 'info') {
        // Create notification element if not exists
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            notificationContainer.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md';
            document.body.appendChild(notificationContainer);
        }

        // Set colors based on notification type
        let bgColor, textColor, borderColor, iconColor;
        switch (type) {
            case 'success':
                bgColor = 'bg-green-50';
                textColor = 'text-green-800';
                borderColor = 'border-green-200';
                iconColor = 'text-green-500';
                break;
            case 'warning':
                bgColor = 'bg-yellow-50';
                textColor = 'text-yellow-800';
                borderColor = 'border-yellow-200';
                iconColor = 'text-yellow-500';
                break;
            case 'error':
                bgColor = 'bg-red-50';
                textColor = 'text-red-800';
                borderColor = 'border-red-200';
                iconColor = 'text-red-500';
                break;
            case 'info':
            default:
                bgColor = 'bg-blue-50';
                textColor = 'text-blue-800';
                borderColor = 'border-blue-200';
                iconColor = 'text-blue-500';
                break;
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `flex items-center p-4 mb-4 rounded-lg border ${bgColor} ${textColor} ${borderColor} shadow-md transform transition-all duration-300 opacity-0 translate-x-full`;

        // Notification content
        notification.innerHTML = `
            <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg ${bgColor} ${iconColor}">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                </svg>
            </div>
            <div class="ml-3 text-sm font-medium">
                <div class="font-bold">${title}</div>
                <div>${message}</div>
            </div>
            <button type="button" class="ml-auto -mx-1.5 -my-1.5 ${bgColor} ${textColor} rounded-lg focus:ring-2 focus:ring-blue-400 p-1.5 hover:bg-blue-200 inline-flex h-8 w-8 items-center justify-center" aria-label="Close">
                <span class="sr-only">Close</span>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;

        // Add to the container
        notificationContainer.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.remove('opacity-0', 'translate-x-full');
        }, 10);

        // Add close button functionality
        const closeButton = notification.querySelector('button');
        closeButton.addEventListener('click', () => {
            notification.classList.add('opacity-0', 'translate-x-full');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (notification.isConnected) {
                notification.classList.add('opacity-0', 'translate-x-full');
                setTimeout(() => {
                    if (notification.isConnected) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
});