// Market Cycle Tracker Application
class MarketCycleTracker {
    constructor() {
        this.currentData = null;
        this.historicalData = null;
        
        this.init();
    }
    
    async init() {
        try {
            // Load data
            await this.loadData();
            
            // Update UI elements
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
                // Fallback to sample data if file doesn't exist yet
                this.currentData = {
                    date: new Date().toISOString(),
                    pe_ratio: 29.6,
                    percentile: 85,
                    status: 'expensive',
                    expected_10yr_return: '3-5%'
                };
            }
            
            // Try to load monthly historical data first
            const monthlyResponse = await fetch('data/monthly_sp500.csv');
            if (monthlyResponse.ok) {
                const csvText = await monthlyResponse.text();
                this.historicalData = this.parseCSV(csvText);
                console.log(`Loaded ${this.historicalData.length} monthly data points`);
            } else {
                // Fallback to annual historical data
                const historicalResponse = await fetch('data/historical_sp500.csv');
                if (historicalResponse.ok) {
                    const csvText = await historicalResponse.text();
                    this.historicalData = this.parseCSV(csvText);
                    console.log(`Loaded ${this.historicalData.length} annual data points`);
                } else {
                    // Generate sample historical data
                    this.historicalData = this.generateSampleHistoricalData();
                    console.log('Using generated sample data');
                }
            }
            
        } catch (error) {
            console.error('Error loading data:', error);
            // Use fallback data
            this.currentData = {
                date: new Date().toISOString(),
                pe_ratio: 29.6,
                percentile: 85,
                status: 'expensive',
                expected_10yr_return: '3-5%'
            };
            this.historicalData = this.generateSampleHistoricalData();
        }
    }
    
    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        
        return lines.slice(1).map(line => {
            const values = line.split(',');
            const row = {};
            headers.forEach((header, index) => {
                row[header.trim()] = values[index] ? values[index].trim() : '';
            });
            return row;
        });
    }
    
    generateSampleHistoricalData() {
        // Generate sample data for demonstration
        const data = [];
        const startYear = 1980;
        const endYear = 2024;
        
        for (let year = startYear; year <= endYear; year++) {
            // Create realistic PE ratios with some volatility
            let pe;
            if (year < 1995) pe = 10 + Math.random() * 8;  // Lower PEs in 80s/early 90s
            else if (year < 2002) pe = 15 + Math.random() * 20; // Bubble period
            else if (year < 2008) pe = 12 + Math.random() * 10; // Post-bubble
            else if (year < 2010) pe = 8 + Math.random() * 12;  // Financial crisis
            else pe = 15 + Math.random() * 12; // Recent era
            
            data.push({
                year: year,
                pe_ratio: Math.round(pe * 10) / 10
            });
        }
        
        return data;
    }
    
    refreshVisualizations() {
        // Add timestamp to force refresh of images when data updates
        const timestamp = new Date().getTime();
        
        const gaugeImg = document.getElementById('marketGauge');
        const cycleImg = document.getElementById('marketCycleChart');
        
        if (gaugeImg) {
            gaugeImg.src = `market_gauge.png?t=${timestamp}`;
        }
        
        if (cycleImg) {
            cycleImg.src = `market_cycle_chart.png?t=${timestamp}`;
        }
    }
    
    
    updateMetrics() {
        if (!this.currentData) return;
        
        // Update current PE
        const peElement = document.getElementById('currentPE');
        if (peElement) {
            peElement.textContent = this.currentData.pe_ratio.toFixed(1);
        }
        
        // Update percentile rank
        const percentileElement = document.getElementById('percentileRank');
        if (percentileElement) {
            percentileElement.textContent = `${this.currentData.percentile}th`;
        }
        
        // Update historical average
        const avgElement = document.getElementById('historicalAvg');
        if (avgElement) {
            const avg = this.calculateHistoricalAverage();
            avgElement.textContent = avg.toFixed(1);
        }
        
        // Update expected return
        const returnElement = document.getElementById('expectedReturn');
        if (returnElement) {
            returnElement.textContent = this.currentData.expected_10yr_return;
        }
        
        // Update last update
        const updateElement = document.getElementById('lastUpdate');
        if (updateElement) {
            const date = new Date(this.currentData.date);
            updateElement.textContent = date.toLocaleDateString();
        }
    }
    
    updateStatus() {
        const statusBadge = document.getElementById('statusBadge');
        if (!statusBadge || !this.currentData) return;
        
        const pe = this.currentData.pe_ratio;
        let status, statusClass, statusText;
        
        if (pe < 16) {
            status = 'attractive';
            statusText = 'ATTRACTIVE';
        } else if (pe < 20) {
            status = 'fair';
            statusText = 'FAIR VALUE';
        } else if (pe < 25) {
            status = 'expensive';
            statusText = 'EXPENSIVE';
        } else {
            status = 'very-expensive';
            statusText = 'VERY EXPENSIVE';
        }
        
        statusBadge.className = `status-badge ${status}`;
        statusBadge.querySelector('.status-text').textContent = statusText;
    }
    
    getPEColor(pe) {
        if (pe < 16) return '#22c55e';      // Green - Attractive
        if (pe < 20) return '#f59e0b';      // Amber - Fair
        if (pe < 25) return '#ef4444';      // Red - Expensive
        return '#dc2626';                   // Dark Red - Very Expensive
    }
    
    calculateHistoricalAverage() {
        if (!this.historicalData || this.historicalData.length === 0) return 17.5;
        
        const peValues = this.historicalData
            .map(d => parseFloat(d.pe_ratio || d.PE_Ratio || 0))
            .filter(pe => pe > 0);
        
        const sum = peValues.reduce((acc, pe) => acc + pe, 0);
        return sum / peValues.length;
    }
    
    showError(message) {
        console.error(message);
        
        // Update UI to show error state
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

// Export for potential use in other contexts
window.MarketCycleTracker = MarketCycleTracker;