#!/usr/bin/env python3
"""
Generate market cycle visualization using Shiller CAPE data.
Creates charts showing historical CAPE ratios and the CAPE-to-returns relationship.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

class MarketVisualizationGenerator:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.web_dir = Path(__file__).parent.parent

    def load_data(self):
        """Load historical and current CAPE data."""
        current_file = self.data_dir / 'current_market.json'
        if current_file.exists():
            with open(current_file, 'r') as f:
                self.current_data = json.load(f)
        else:
            self.current_data = {'cape': 38.0, 'pe_ratio': 38.0, 'date': datetime.now().isoformat()}

        hist_file = self.data_dir / 'cape_historical.json'
        if hist_file.exists():
            with open(hist_file, 'r') as f:
                self.historical = json.load(f)
        else:
            self.historical = []

    def create_market_cycle_chart(self):
        """Create the main CAPE historical visualization."""
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Shiller CAPE Ratio: Where Are We Now?',
                     fontsize=18, fontweight='bold', y=0.95)

        if not self.historical:
            ax1.text(0.5, 0.5, 'No historical data available', ha='center', va='center')
            ax2.text(0.5, 0.5, 'No historical data available', ha='center', va='center')
            output_path = self.web_dir / 'market_cycle_chart.png'
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            return output_path

        # Parse dates and CAPE values
        dates = []
        capes = []
        for r in self.historical:
            try:
                year = int(r['date'][:4])
                month = int(r['date'][5:7])
                dates.append(year + (month - 1) / 12)
                capes.append(r['cape'])
            except (ValueError, KeyError):
                continue

        if not dates:
            output_path = self.web_dir / 'market_cycle_chart.png'
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            return output_path

        min_date = min(dates)
        max_date = max(dates) + 1
        date_range = [min_date, max_date]

        # Top chart: CAPE over time with valuation zones
        ax1.fill_between(date_range, 0, 12, alpha=0.15, color='green', label='Screaming Buy (<12)')
        ax1.fill_between(date_range, 12, 20, alpha=0.15, color='#4ade80', label='Attractive (12-20)')
        ax1.fill_between(date_range, 20, 25, alpha=0.15, color='orange', label='Fair Value (20-25)')
        ax1.fill_between(date_range, 25, 35, alpha=0.15, color='red', label='Expensive (25-35)')
        ax1.fill_between(date_range, 35, 50, alpha=0.15, color='darkred', label='Bubble (>35)')

        ax1.plot(dates, capes, linewidth=1.5, color='navy', alpha=0.8)

        # Historical average
        avg_cape = sum(capes) / len(capes)
        ax1.axhline(y=avg_cape, color='purple', linestyle='--', linewidth=2,
                    alpha=0.8, label=f'Historical Average: {avg_cape:.1f}')

        # Current CAPE marker
        current_cape = self.current_data.get('cape', self.current_data.get('pe_ratio', 0))
        current_year = datetime.fromisoformat(self.current_data['date']).year
        ax1.scatter([current_year + 0.1], [current_cape], s=150, color='red',
                   edgecolor='darkred', linewidth=2, zorder=5,
                   label=f'Current CAPE: {current_cape}')

        # Key events
        events = [
            (1929, 'Crash of 1929'),
            (2000, 'Dot-com Peak'),
            (2009, 'GFC Bottom'),
        ]
        for year, event in events:
            nearby = [(d, c) for d, c in zip(dates, capes) if abs(d - year) < 0.5]
            if nearby:
                d, c = nearby[0]
                ax1.annotate(event, xy=(d, c), xytext=(10, 10), textcoords='offset points',
                           fontsize=8, color='darkblue', fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.8))

        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('CAPE Ratio', fontsize=12)
        ax1.set_title('Shiller CAPE Ratio (1881-Present)', fontsize=14)
        ax1.legend(loc='upper left', fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, max(max(capes), current_cape) + 5)

        # Bottom chart: CAPE vs Forward 10-year Real Returns
        scatter_capes = []
        scatter_returns = []
        for r in self.historical:
            if r.get('fwd10yr') is not None:
                scatter_capes.append(r['cape'])
                scatter_returns.append(r['fwd10yr'])

        if scatter_capes:
            ax2.scatter(scatter_capes, scatter_returns, alpha=0.3, s=10, color='steelblue', label='Historical')

            # Regression line
            x_line = np.linspace(5, 50, 100)
            y_line = -0.327 * x_line + 15.42
            ax2.plot(x_line, y_line, color='darkred', linewidth=2.5, label='Regression (R²=0.74)')

            # Current CAPE marker
            implied = -0.327 * current_cape + 15.42
            ax2.scatter([current_cape], [implied], s=200, color='red', marker='*',
                       edgecolor='darkred', linewidth=2, zorder=5,
                       label=f'Current: CAPE {current_cape} → {implied:.1f}%')
        else:
            # If no forward return data, show regression line only
            x_line = np.linspace(5, 50, 100)
            y_line = -0.327 * x_line + 15.42
            ax2.plot(x_line, y_line, color='darkred', linewidth=2.5, label='Regression (R²=0.74)')
            implied = -0.327 * current_cape + 15.42
            ax2.scatter([current_cape], [implied], s=200, color='red', marker='*',
                       edgecolor='darkred', linewidth=2, zorder=5,
                       label=f'Current: CAPE {current_cape} → {implied:.1f}%')

        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_xlabel('Starting CAPE Ratio', fontsize=12)
        ax2.set_ylabel('Subsequent 10-Year Real Return (%)', fontsize=12)
        ax2.set_title('CAPE at Time of Investment vs Actual 10-Year Real Returns', fontsize=14)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)

        # Interpretation
        if current_cape > 35:
            interpretation = "CAPE is in BUBBLE TERRITORY - historically lowest expected returns"
            color = 'darkred'
        elif current_cape > 25:
            interpretation = "CAPE indicates EXPENSIVE valuations - below-average returns expected"
            color = 'red'
        elif current_cape > 20:
            interpretation = "CAPE at FAIR VALUE - moderate returns expected"
            color = 'orange'
        else:
            interpretation = "CAPE indicates ATTRACTIVE valuations - above-average returns expected"
            color = 'green'

        fig.text(0.5, 0.02, interpretation, ha='center', fontsize=14,
                fontweight='bold', color=color,
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.1, top=0.9)

        output_path = self.web_dir / 'market_cycle_chart.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return output_path

    def create_gauge_alternative(self):
        """Create a CAPE gauge visualization."""
        fig, ax = plt.subplots(figsize=(8, 4))
        current_cape = self.current_data.get('cape', self.current_data.get('pe_ratio', 38))

        zones = [
            (0, 12, 'Screaming Buy', '#16a34a'),
            (12, 20, 'Attractive', '#22c55e'),
            (20, 25, 'Fair Value', '#f59e0b'),
            (25, 35, 'Expensive', '#ef4444'),
            (35, 50, 'Bubble', '#991b1b'),
        ]

        for i, (min_val, max_val, label, color) in enumerate(zones):
            ax.barh(i, max_val - min_val, left=min_val, height=0.6,
                   color=color, alpha=0.3, edgecolor='black')
            ax.text(min_val + (max_val - min_val)/2, i, f'{label}\n({min_val}-{max_val})',
                   ha='center', va='center', fontweight='bold', fontsize=9)

        for i, (min_val, max_val, _, _) in enumerate(zones):
            if min_val <= current_cape < max_val:
                ax.scatter([current_cape], [i], s=200, color='darkred',
                          marker='v', edgecolor='black', linewidth=2, zorder=5)
                ax.text(current_cape, i-0.4, f'Current\n{current_cape}',
                       ha='center', va='top', fontweight='bold', color='darkred')
                break

        ax.set_xlim(0, 50)
        ax.set_ylim(-0.5, len(zones) - 0.5)
        ax.set_xlabel('CAPE Ratio', fontsize=12)
        ax.set_title('Market Valuation Gauge (Shiller CAPE)', fontsize=14, fontweight='bold')
        ax.set_yticks([])
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        gauge_path = self.web_dir / 'market_gauge.png'
        plt.savefig(gauge_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return gauge_path

    def generate_all_visualizations(self):
        """Generate all visualizations."""
        print("Loading data...")
        self.load_data()
        print("Generating CAPE history chart...")
        cycle_chart = self.create_market_cycle_chart()
        print("Generating CAPE gauge...")
        gauge_chart = self.create_gauge_alternative()
        print(f"Visualizations saved:")
        print(f"  Chart: {cycle_chart}")
        print(f"  Gauge: {gauge_chart}")
        return cycle_chart, gauge_chart

def main():
    generator = MarketVisualizationGenerator()
    generator.generate_all_visualizations()
    print("Done!")

if __name__ == "__main__":
    main()
