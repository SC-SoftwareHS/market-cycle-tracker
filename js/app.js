// Market Cycle Tracker Application - CAPE (Shiller PE) Based
class MarketCycleTracker {
    constructor() {
        this.currentData = null;
        this.historicalData = null;
        this.init();
    }

    async init() {
        try {
            await this.loadData();
            this.updateMetrics();
            this.updateStatus();
            this.refreshVisualizations();
        } catch (error) {
            console.error('Failed to initialize Market Cycle Tracker:', error);
            this.showError('Failed to load market data. Please try refreshing the page.');
        }
    }

    async loadData() {
        try {
            // Load current market data
            const currentResponse = await fetch('data/current_market.json');
            if (currentResponse.ok) {
                this.currentData = await currentResponse.json();
            } else {
                this.currentData = this.getFallbackData();
            }

            // Load CAPE historical data (JSON format, 1881-present)
            const histResponse = await fetch('data/cape_historical.json');
            if (histResponse.ok) {
                this.historicalData = await histResponse.json();
                console.log(`Loaded ${this.historicalData.length} monthly CAPE records`);
            } else {
                this.historicalData = [];
                console.log('No historical CAPE data available');
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.currentData = this.getFallbackData();
            this.historicalData = [];
        }
    }

    getFallbackData() {
        return {
            date: new Date().toISOString(),
            cape: 38.0,
            pe_ratio: 38.0,
            percentile: 97,
            status: 'bubble',
            status_text: 'BUBBLE TERRITORY',
            expected_10yr_return: '2%',
            historical_average: 17.8,
            condition: 'Bubble Territory',
            impliedReturn: 2.97,
            earningsYield: 2.63,
        };
    }

    refreshVisualizations() {
        const timestamp = new Date().getTime();
        const gaugeImg = document.getElementById('marketGauge');
        const cycleImg = document.getElementById('marketCycleChart');
        if (gaugeImg) gaugeImg.src = `market_gauge.png?t=${timestamp}`;
        if (cycleImg) cycleImg.src = `market_cycle_chart.png?t=${timestamp}`;
    }

    updateMetrics() {
        if (!this.currentData) return;

        // Update current CAPE
        const peElement = document.getElementById('currentPE');
        if (peElement) {
            const cape = this.currentData.cape || this.currentData.pe_ratio;
            peElement.textContent = cape.toFixed(1);
        }

        // Update percentile rank
        const percentileElement = document.getElementById('percentileRank');
        if (percentileElement) {
            const pct = this.currentData.percentile;
            percentileElement.textContent = typeof pct === 'number' ? `${pct}th` : `${pct}`;
        }

        // Update historical average
        const avgElement = document.getElementById('historicalAvg');
        if (avgElement) {
            const avg = this.currentData.historical_average || this.calculateHistoricalAverage();
            avgElement.textContent = avg.toFixed(1);
        }

        // Update expected return
        const returnElement = document.getElementById('expectedReturn');
        if (returnElement) {
            if (this.currentData.impliedReturn !== undefined) {
                returnElement.textContent = `${this.currentData.impliedReturn}%`;
            } else {
                returnElement.textContent = this.currentData.expected_10yr_return;
            }
        }

        // Update last update
        const updateElement = document.getElementById('lastUpdate');
        if (updateElement) {
            const date = new Date(this.currentData.date);
            updateElement.textContent = date.toLocaleDateString();
        }

        // Update condition text if element exists
        const conditionElement = document.getElementById('conditionText');
        if (conditionElement && this.currentData.condition) {
            conditionElement.textContent = this.currentData.condition;
        }

        // Update earnings yield if element exists
        const eyElement = document.getElementById('earningsYield');
        if (eyElement && this.currentData.earningsYield) {
            eyElement.textContent = `${this.currentData.earningsYield}%`;
        }
    }

    updateStatus() {
        const statusBadge = document.getElementById('statusBadge');
        if (!statusBadge || !this.currentData) return;

        const cape = this.currentData.cape || this.currentData.pe_ratio;
        let status, statusText;

        if (cape < 12) {
            status = 'screaming-buy';
            statusText = 'SCREAMING BUY';
        } else if (cape < 16) {
            status = 'very-attractive';
            statusText = 'VERY ATTRACTIVE';
        } else if (cape < 20) {
            status = 'attractive';
            statusText = 'ATTRACTIVE';
        } else if (cape < 25) {
            status = 'fair';
            statusText = 'FAIR VALUE';
        } else if (cape < 30) {
            status = 'expensive';
            statusText = 'EXPENSIVE';
        } else if (cape < 35) {
            status = 'very-expensive';
            statusText = 'VERY EXPENSIVE';
        } else {
            status = 'bubble';
            statusText = 'BUBBLE TERRITORY';
        }

        // Use server-provided status if available
        if (this.currentData.status) {
            status = this.currentData.status;
        }
        if (this.currentData.status_text) {
            statusText = this.currentData.status_text;
        }

        statusBadge.className = `status-badge ${status}`;
        statusBadge.querySelector('.status-text').textContent = statusText;
    }

    calculateHistoricalAverage() {
        if (!this.historicalData || this.historicalData.length === 0) return 17.8;
        const capeValues = this.historicalData
            .map(d => parseFloat(d.cape || 0))
            .filter(c => c > 0);
        if (capeValues.length === 0) return 17.8;
        const sum = capeValues.reduce((acc, c) => acc + c, 0);
        return sum / capeValues.length;
    }

    showError(message) {
        console.error(message);
        const peElement = document.getElementById('currentPE');
        if (peElement) peElement.textContent = 'Error';
        const statusBadge = document.getElementById('statusBadge');
        if (statusBadge) {
            statusBadge.className = 'status-badge';
            statusBadge.querySelector('.status-text').textContent = 'Data unavailable';
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MarketCycleTracker();
});

window.MarketCycleTracker = MarketCycleTracker;
