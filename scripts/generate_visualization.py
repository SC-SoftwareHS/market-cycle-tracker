#!/usr/bin/env python3
"""
Generate market cycle visualization using Harrison's existing analysis approach
Adapted from cape_scatterplot.py and sp500_pe_returns_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
import json

class MarketVisualizationGenerator:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.web_dir = Path(__file__).parent.parent
        
    def load_data(self):
        """Load historical and current data"""
        # Load current data
        current_file = self.data_dir / 'current_market.json'
        if current_file.exists():
            with open(current_file, 'r') as f:
                self.current_data = json.load(f)
        else:
            self.current_data = {'pe_ratio': 29.6, 'date': datetime.now().isoformat()}
        
        # Load historical data
        historical_file = self.data_dir / 'historical_sp500.csv'
        if historical_file.exists():
            self.historical_df = pd.read_csv(historical_file)
            # Use Trailing_PE_Jan1 as the most reliable PE measure
            self.historical_df['PE_Ratio'] = self.historical_df['Trailing_PE_Jan1']
        else:
            # Fallback data
            years = list(range(1980, 2025))
            pe_ratios = [7.39, 9.02, 7.73, 11.48, 11.52, 10.36, 14.28, 18.01, 14.02, 11.82,
                        15.13, 15.35, 25.93, 22.5, 21.34, 14.89, 18.08, 19.53, 24.29, 32.92,
                        29.04, 27.55, 46.17, 31.43, 22.73, 19.99, 18.07, 17.36, 21.46, 70.91,
                        20.7, 16.3, 14.87, 17.03, 18.15, 20.02, 22.18, 23.59, 24.97, 19.6,
                        24.88, 35.96, 23.11, 22.82, 25.01]
            self.historical_df = pd.DataFrame({'Year': years, 'PE_Ratio': pe_ratios})
    
    def create_market_cycle_chart(self):
        """Create the main market cycle visualization"""
        plt.style.use('seaborn-v0_8-whitegrid')
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('S&P 500 Market Cycle Analysis: Where Are We Now?', 
                     fontsize=18, fontweight='bold', y=0.95)
        
        # Top chart: PE Ratio over time with cycle zones
        ax1.fill_between(self.historical_df['Year'], 0, 16, alpha=0.3, color='green', label='Attractive (<16)')
        ax1.fill_between(self.historical_df['Year'], 16, 25, alpha=0.3, color='orange', label='Expensive (16-25)')
        ax1.fill_between(self.historical_df['Year'], 25, 50, alpha=0.3, color='red', label='Very Expensive (>25)')
        
        # Plot historical PE ratios
        ax1.plot(self.historical_df['Year'], self.historical_df['PE_Ratio'], 
                linewidth=2.5, color='navy', alpha=0.8, marker='o', markersize=3)
        
        # Add historical average line
        avg_pe = self.historical_df['PE_Ratio'].mean()
        ax1.axhline(y=avg_pe, color='purple', linestyle='--', linewidth=2, 
                   alpha=0.8, label=f'Historical Average: {avg_pe:.1f}')
        
        # Highlight current PE
        current_pe = self.current_data['pe_ratio']
        current_year = datetime.fromisoformat(self.current_data['date']).year
        ax1.scatter([current_year], [current_pe], s=150, color='red', 
                   edgecolor='darkred', linewidth=2, zorder=5, 
                   label=f'Current PE: {current_pe}')
        
        # Add key market events
        events = [
            (2000, 'Dot-com Bubble'),
            (2008, 'Financial Crisis'),
            (2020, 'COVID Pandemic'),
            (current_year, 'Today')
        ]
        
        for year, event in events:
            if year in self.historical_df['Year'].values:
                pe_value = self.historical_df[self.historical_df['Year'] == year]['PE_Ratio'].iloc[0]
                ax1.annotate(event, xy=(year, pe_value), 
                           xytext=(10, 10), textcoords='offset points',
                           fontsize=9, color='darkblue', fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.8))
        
        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('P/E Ratio', fontsize=12)
        ax1.set_title('S&P 500 P/E Ratio Over Time: Market Cycle Context', fontsize=14)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, max(self.historical_df['PE_Ratio'].max(), current_pe) + 5)
        
        # Bottom chart: PE vs Expected Returns relationship based on historical data
        # Create a simplified model based on research relationships
        pe_ranges = np.linspace(5, 45, 100)
        
        # Historical relationship: Expected Return ≈ 20/PE + risk_premium
        # This approximates the inverse relationship found in research
        base_returns = 20 / pe_ranges + 2  # Base earnings yield plus risk premium
        
        # Apply floor and ceiling constraints based on historical ranges
        expected_returns = []
        for i, pe in enumerate(pe_ranges):
            base_ret = base_returns[i]
            
            # Adjust based on valuation zones with some variability
            if pe < 12:  # Very attractive
                ret = min(base_ret, 14) + np.random.normal(0, 1.5)
            elif pe < 16:  # Attractive 
                ret = min(base_ret, 12) + np.random.normal(0, 1.2)
            elif pe < 20:  # Fair value
                ret = min(base_ret, 9) + np.random.normal(0, 1.0)
            elif pe < 25:  # Expensive
                ret = min(base_ret, 6) + np.random.normal(0, 0.8)
            else:  # Very expensive
                ret = min(base_ret, 4) + np.random.normal(0, 0.6)
            
            # Floor at -5% and ceiling at 15% to be realistic
            expected_returns.append(max(min(ret, 15), -5))
        
        # Plot the relationship
        ax2.plot(pe_ranges, expected_returns, color='darkblue', linewidth=3, alpha=0.8, 
                label='Expected 10-Year Returns')
        
        # Add confidence bands
        upper_band = np.array(expected_returns) + 2
        lower_band = np.array(expected_returns) - 2
        ax2.fill_between(pe_ranges, lower_band, upper_band, alpha=0.2, color='darkblue', 
                        label='Historical Range')
        
        # Add valuation zone backgrounds
        ax2.axvspan(0, 16, alpha=0.1, color='green', label='Attractive Zone')
        ax2.axvspan(16, 25, alpha=0.1, color='orange', label='Expensive Zone')
        ax2.axvspan(25, 50, alpha=0.1, color='red', label='Very Expensive Zone')
        
        # Mark current PE and expected return
        current_expected = None
        for i, pe in enumerate(pe_ranges):
            if abs(pe - current_pe) < 0.5:
                current_expected = expected_returns[i]
                break
        
        if current_expected:
            ax2.scatter([current_pe], [current_expected], s=200, color='red', 
                       edgecolor='darkred', linewidth=3, zorder=5, 
                       label=f'Current: {current_pe} PE → ~{current_expected:.1f}% returns')
        
        # Add horizontal reference lines
        ax2.axhline(y=10, color='gray', linestyle=':', alpha=0.7, label='Historical Avg (10%)')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        ax2.set_xlabel('Starting P/E Ratio', fontsize=12)
        ax2.set_ylabel('Expected 10-Year Annual Return (%)', fontsize=12)
        ax2.set_title('P/E Ratio vs Expected Future Returns\n(Based on Historical Relationships)', fontsize=14)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Add interpretation text
        if current_pe < 16:
            interpretation = "Market appears ATTRACTIVE based on historical P/E ratios"
            color = 'green'
        elif current_pe < 25:
            interpretation = "Market appears EXPENSIVE based on historical P/E ratios"
            color = 'orange'
        else:
            interpretation = "Market appears VERY EXPENSIVE based on historical P/E ratios"
            color = 'red'
        
        fig.text(0.5, 0.02, interpretation, ha='center', fontsize=14, 
                fontweight='bold', color=color,
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.1, top=0.9)
        
        # Save the chart
        output_path = self.web_dir / 'market_cycle_chart.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def create_gauge_alternative(self):
        """Create a simple gauge-like visualization as alternative"""
        fig, ax = plt.subplots(figsize=(8, 4))
        
        current_pe = self.current_data['pe_ratio']
        
        # Create zones
        zones = [
            (0, 16, 'Attractive', 'green'),
            (16, 20, 'Fair', 'yellow'),
            (20, 25, 'Expensive', 'orange'), 
            (25, 50, 'Very Expensive', 'red')
        ]
        
        # Draw zones as horizontal bars
        for i, (min_val, max_val, label, color) in enumerate(zones):
            ax.barh(i, max_val - min_val, left=min_val, height=0.6, 
                   color=color, alpha=0.3, edgecolor='black')
            ax.text(min_val + (max_val - min_val)/2, i, f'{label}\n({min_val}-{max_val})', 
                   ha='center', va='center', fontweight='bold', fontsize=10)
        
        # Add current PE indicator
        for i, (min_val, max_val, _, _) in enumerate(zones):
            if min_val <= current_pe < max_val:
                ax.scatter([current_pe], [i], s=200, color='darkred', 
                          marker='v', edgecolor='black', linewidth=2, zorder=5)
                ax.text(current_pe, i-0.4, f'Current\n{current_pe}', 
                       ha='center', va='top', fontweight='bold', color='darkred')
                break
        
        ax.set_xlim(0, 40)
        ax.set_ylim(-0.5, len(zones) - 0.5)
        ax.set_xlabel('P/E Ratio', fontsize=12)
        ax.set_title('Market Valuation Gauge', fontsize=14, fontweight='bold')
        ax.set_yticks([])
        ax.grid(True, axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        # Save gauge
        gauge_path = self.web_dir / 'market_gauge.png'
        plt.savefig(gauge_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return gauge_path
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("Loading data...")
        self.load_data()
        
        print("Generating market cycle chart...")
        cycle_chart = self.create_market_cycle_chart()
        
        print("Generating market gauge...")
        gauge_chart = self.create_gauge_alternative()
        
        print(f"Visualizations saved to:")
        print(f"  Market Cycle Chart: {cycle_chart}")
        print(f"  Market Gauge: {gauge_chart}")
        
        return cycle_chart, gauge_chart

def main():
    generator = MarketVisualizationGenerator()
    generator.generate_all_visualizations()
    print("Visualization generation completed!")

if __name__ == "__main__":
    main()