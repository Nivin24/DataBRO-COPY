document.addEventListener('DOMContentLoaded', function() {
    fetchDashboardData();
});

async function fetchDashboardData() {
    try {
        const response = await fetch('/api/dashboard-data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Populate metrics
        document.getElementById('total-members').textContent = data.total_members;
        document.getElementById('active-users').textContent = data.active_users_last_7_days;
        document.getElementById('new-signups').textContent = data.new_signups_last_30_days;

        // Render DAU Trend Chart
        const dauCtx = document.getElementById('dauTrendChart').getContext('2d');
        new Chart(dauCtx, {
            type: 'line', // or 'bar'
            data: {
                labels: data.dau_trend.labels,
                datasets: [{
                    label: 'Daily Active Users',
                    data: data.dau_trend.values,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Populate Recent Users Table
        const usersTableBody = document.querySelector('#recent-users-table tbody');
        usersTableBody.innerHTML = ''; // Clear loading message

        if (data.recent_users && data.recent_users.length > 0) {
            data.recent_users.forEach(user => {
                const row = usersTableBody.insertRow();
                row.innerHTML = `
                    <td><img src="${user.profile_pic}" alt="Profile Pic" class="profile-pic"></td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>${user.joined}</td>
                    <td>${user.last_login}</td>
                `;
            });
        } else {
            usersTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No recent user activity to display.</td></tr>';
        }

    } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
        // Display error messages on the dashboard if needed
        document.getElementById('total-members').textContent = 'Error';
        document.getElementById('active-users').textContent = 'Error';
        document.getElementById('new-signups').textContent = 'Error';
        const usersTableBody = document.querySelector('#recent-users-table tbody');
        usersTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Error loading user data.</td></tr>';
    }
}