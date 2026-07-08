document.addEventListener('DOMContentLoaded', () => {
    const btnHealthy = document.getElementById('sendHealthyBtn');
    const btnFailure = document.getElementById('sendFailureBtn');
    const card = document.getElementById('statusCard');
    const statusText = document.getElementById('statusText');
    const probText = document.getElementById('probabilityText');
    const overlay = document.getElementById('loadingOverlay');
    const s1Val = document.getElementById('s1_val');
    const s2Val = document.getElementById('s2_val');

    // These values match the schema in api/index.py
    const healthyData = {
        sensor_1_mean: 0.1, sensor_1_std: 1.0, sensor_1_min: -1.5, sensor_1_max: 1.5, 
        sensor_1_last: 0.2, sensor_1_range: 3.0, sensor_1_trend: 0.1, sensor_1_abs_change: 0.5, sensor_1_variance: 1.0,
        sensor_2_mean: 5.0, sensor_2_std: 2.0, sensor_2_min: 1.0, sensor_2_max: 9.0, 
        sensor_2_last: 5.2, sensor_2_range: 8.0, sensor_2_trend: 0.2, sensor_2_abs_change: 1.0, sensor_2_variance: 4.0
    };

    // Data with high variances/trends to trigger a failure prediction
    const failureData = {
        sensor_1_mean: 4.5, sensor_1_std: 5.2, sensor_1_min: -5.1, sensor_1_max: 12.5, 
        sensor_1_last: 10.8, sensor_1_range: 17.6, sensor_1_trend: 8.3, sensor_1_abs_change: 3.2, sensor_1_variance: 27.04,
        sensor_2_mean: 15.5, sensor_2_std: 8.1, sensor_2_min: 2.1, sensor_2_max: 28.5, 
        sensor_2_last: 25.8, sensor_2_range: 26.4, sensor_2_trend: 12.3, sensor_2_abs_change: 4.5, sensor_2_variance: 65.61
    };

    async function sendData(data, type) {
        // UI Loading State
        overlay.classList.add('active');
        s1Val.innerText = data.sensor_1_mean.toFixed(2);
        s2Val.innerText = data.sensor_2_mean.toFixed(2);
        
        card.className = 'card status-card'; // reset classes
        statusText.innerText = 'Analyzing...';
        statusText.style.color = 'var(--text-primary)';
        probText.innerText = 'Running Random Forest inference...';

        try {
            // Because we are on the same domain in Vercel, we can just hit /api/predict
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            // Give a slight delay for smooth UI animation
            setTimeout(() => {
                overlay.classList.remove('active');
                
                // We use probability_failure if available, otherwise fallback to the raw prediction
                const prob = result.probability_failure !== undefined 
                    ? result.probability_failure 
                    : (result.prediction === 1 ? 1.0 : 0.0);
                
                const percentage = (prob * 100).toFixed(1);

                if (result.prediction === 1 || prob > 0.5) {
                    card.classList.add('status-critical');
                    statusText.innerText = 'Critical Failure Imminent';
                    statusText.style.color = 'var(--danger)';
                    probText.innerText = `Probability of Failure: ${percentage}%`;
                } else {
                    card.classList.add('status-healthy');
                    statusText.innerText = 'System Healthy';
                    statusText.style.color = 'var(--success)';
                    probText.innerText = `Probability of Failure: ${percentage}%`;
                }
            }, 800);

        } catch (error) {
            console.error('Error:', error);
            setTimeout(() => {
                overlay.classList.remove('active');
                statusText.innerText = 'Connection Error';
                probText.innerText = 'Failed to reach API endpoint.';
            }, 800);
        }
    }

    btnHealthy.addEventListener('click', () => sendData(healthyData, 'healthy'));
    btnFailure.addEventListener('click', () => sendData(failureData, 'failure'));

    // Manual Entry Logic
    const manualBtn = document.getElementById('manualEntryBtn');
    const manualModal = document.getElementById('manualModal');
    const closeBtn = document.getElementById('closeModalBtn');
    const manualForm = document.getElementById('manualForm');

    manualBtn.addEventListener('click', () => {
        manualModal.classList.add('active');
    });

    closeBtn.addEventListener('click', () => {
        manualModal.classList.remove('active');
    });

    // Close when clicking outside
    manualModal.addEventListener('click', (e) => {
        if (e.target === manualModal) {
            manualModal.classList.remove('active');
        }
    });

    manualForm.addEventListener('submit', (e) => {
        e.preventDefault();
        manualModal.classList.remove('active');
        
        const manualData = {
            sensor_1_mean: parseFloat(document.getElementById('s1_mean').value) || 0,
            sensor_1_std: parseFloat(document.getElementById('s1_std').value) || 0,
            sensor_1_min: parseFloat(document.getElementById('s1_min').value) || 0,
            sensor_1_max: parseFloat(document.getElementById('s1_max').value) || 0,
            sensor_1_last: parseFloat(document.getElementById('s1_last').value) || 0,
            sensor_1_range: parseFloat(document.getElementById('s1_range').value) || 0,
            sensor_1_trend: parseFloat(document.getElementById('s1_trend').value) || 0,
            sensor_1_abs_change: parseFloat(document.getElementById('s1_change').value) || 0,
            sensor_1_variance: parseFloat(document.getElementById('s1_var').value) || 0,
            
            sensor_2_mean: parseFloat(document.getElementById('s2_mean').value) || 0,
            sensor_2_std: parseFloat(document.getElementById('s2_std').value) || 0,
            sensor_2_min: parseFloat(document.getElementById('s2_min').value) || 0,
            sensor_2_max: parseFloat(document.getElementById('s2_max').value) || 0,
            sensor_2_last: parseFloat(document.getElementById('s2_last').value) || 0,
            sensor_2_range: parseFloat(document.getElementById('s2_range').value) || 0,
            sensor_2_trend: parseFloat(document.getElementById('s2_trend').value) || 0,
            sensor_2_abs_change: parseFloat(document.getElementById('s2_change').value) || 0,
            sensor_2_variance: parseFloat(document.getElementById('s2_var').value) || 0
        };
        
        sendData(manualData, 'manual');
    });
});
