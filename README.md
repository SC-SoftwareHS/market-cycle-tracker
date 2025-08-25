# Market Cycle Tracker

A simple, clean visualization tool that answers one key question: **"Where are we in the S&P 500 market cycle?"**

This tool tracks the S&P 500 Price-to-Earnings (PE) ratio and provides context based on historical data and institutional research from sources like JP Morgan's Guide to the Markets.

## 🎯 Purpose

- **Simple Market Assessment**: Get an instant view of current market valuations
- **Historical Context**: See where current valuations rank vs. historical norms
- **Return Expectations**: Understand what history suggests about future returns
- **Blog Integration**: Embed in blog posts or use as a standalone resource

## ⚡ Key Features

- **Daily Updates**: Automatically scrapes current PE data via GitHub Actions
- **Historical Context**: Current PE vs. 45 years of historical data (1980-2024)
- **Clean Visualization**: Simple gauge showing valuation zones
- **Mobile Responsive**: Works on all devices
- **Embeddable**: Lightweight widget for blog posts
- **No Backend Required**: Static site with automated data updates

## 📊 Current Market Reading

The tool shows the S&P 500 PE ratio in context:

- **Green (Attractive)**: PE < 16 - Expected 10yr returns: 8-12%
- **Yellow (Fair Value)**: PE 16-20 - Expected 10yr returns: 5-8%
- **Orange (Expensive)**: PE 20-25 - Expected 10yr returns: 3-5%
- **Red (Very Expensive)**: PE > 25 - Expected 10yr returns: 0-3%

## 🚀 Quick Start

### Option 1: Use in Your Blog (Recommended)

**For Astro blogs** (like harrisonstoneham.com):

1. Copy the `embed.html` file to your blog's public assets
2. Embed in your blog post:

```astro
---
// In your .astro file
---

<iframe 
  src="/market-cycle-tracker/embed.html" 
  width="100%" 
  height="400" 
  frameborder="0"
  title="Market Cycle Tracker">
</iframe>
```

**For other platforms:**
```html
<iframe 
  src="https://yourusername.github.io/market-cycle-tracker/embed.html" 
  width="100%" 
  height="400" 
  frameborder="0">
</iframe>
```

### Option 2: Standalone Site

1. Upload all files to your web server or GitHub Pages
2. Enable GitHub Actions for daily data updates
3. Visit `index.html` for the full experience

## 📁 Project Structure

```
market-cycle-tracker/
├── index.html              # Main dashboard
├── embed.html              # Lightweight embed version
├── css/
│   └── style.css          # All styling
├── js/
│   └── app.js             # Application logic & charts
├── data/
│   ├── current_market.json      # Daily updated market data
│   ├── historical_sp500.csv     # Historical PE ratios (1980-2024)
│   └── jp_morgan_ranges.json    # Valuation ranges & references
├── scripts/
│   └── update_market_data.py    # Data scraping script
└── .github/workflows/
    └── update_data.yml         # Daily automation
```

## 🔄 How Data Updates Work

1. **GitHub Action** runs daily at 4:30 PM EST (after market close)
2. **Python script** scrapes current PE ratio from multpl.com
3. **Calculates percentile** vs. historical data
4. **Updates JSON file** with new market data
5. **Commits changes** back to repository

### Manual Update

```bash
cd scripts
python update_market_data.py
```

## 📈 Data Sources

- **Current PE Ratio**: [multpl.com/s-p-500-pe-ratio](https://www.multpl.com/s-p-500-pe-ratio)
- **Historical Data**: S&P 500 earnings reports (1980-2024)
- **Return Expectations**: Based on JP Morgan Asset Management research
- **Valuation Framework**: Institutional research and historical analysis

## 🛠️ Technology Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Charts**: Chart.js for visualizations  
- **Data Updates**: Python + BeautifulSoup + GitHub Actions
- **Hosting**: Static files (works anywhere)
- **No dependencies**: Runs without backend or database

## 🎨 Customization

### Change Valuation Thresholds

Edit the ranges in `js/app.js`:

```javascript
// Current thresholds
if (pe < 16) status = 'attractive';      // 8-12% expected returns
else if (pe < 20) status = 'fair';       // 5-8% expected returns  
else if (pe < 25) status = 'expensive';  // 3-5% expected returns
else status = 'very-expensive';          // 0-3% expected returns
```

### Modify Colors

Update CSS variables in `css/style.css`:

```css
:root {
    --attractive-color: #22c55e;      /* Green */
    --fair-color: #f59e0b;           /* Amber */
    --expensive-color: #ef4444;       /* Red */
    --very-expensive-color: #dc2626;  /* Dark Red */
}
```

### Add New Data Sources

Extend the scraper in `scripts/update_market_data.py`:

```python
def scrape_alternative_source(self):
    # Add new data source here
    pass
```

## 📱 Embed Integration Examples

### Markdown Blog Post

```markdown
## Current Market Valuation

<iframe src="/market-cycle-tracker/embed.html" 
        width="100%" height="400" frameborder="0">
</iframe>

As you can see above, the current S&P 500 PE ratio of 29.6 puts us in expensive territory...
```

### WordPress

```html
[iframe src="/market-cycle-tracker/embed.html" width="100%" height="400"]
```

### Ghost/Substack

Use the HTML embed block with the iframe code.

## ⚖️ Important Disclaimers

- **Not Investment Advice**: This tool is for educational purposes only
- **Past Performance**: Historical relationships may not continue
- **Timing Limitations**: PE ratios can stay elevated/depressed for years
- **Consult Professionals**: Always seek qualified financial advice

## 🤝 Contributing

1. **Fork** the repository
2. **Make changes** to improve accuracy or usability
3. **Test** with your own data
4. **Submit pull request** with clear description

### Ideas for Contributions

- [ ] Add CAPE ratio as alternative metric
- [ ] Include sector PE breakdowns  
- [ ] Add international market comparisons
- [ ] Improve mobile responsiveness
- [ ] Add more data sources for reliability

## 📄 License

MIT License - feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- **JP Morgan Asset Management** for valuation research and frameworks
- **Robert Shiller** for CAPE ratio methodology  
- **multpl.com** for reliable PE ratio data
- **Chart.js** for beautiful, simple charts

---

**Built for**: Blog integration and educational purposes  
**Maintained by**: Harrison Stoneham ([harrisonstoneham.com](https://harrisonstoneham.com))  
**Source Code**: Open source on GitHub for full transparency  

*"We never know where we're going, but we ought to know where we are."*