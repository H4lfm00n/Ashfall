# Emotionless Options Predictor

A sophisticated options analysis and prediction system that combines data scraping, sentiment analysis, and machine learning to provide objective options trading insights.

## Features

- **Comprehensive Options Data Collection**
  - Real-time options chain data from multiple sources
  - Greeks calculation (delta, gamma, theta, vega, rho)
  - Volume and open interest analysis
  - Implied volatility metrics
  - Historical options data

- **Advanced Analysis**
  - Market condition analysis
  - Risk metrics calculation
  - Strategy recommendations
  - Performance simulation
  - Position sizing optimization

- **Sentiment Analysis**
  - News sentiment analysis
  - Social media sentiment tracking
  - Market sentiment indicators
  - Sentiment-based strategy adjustments

## Project Structure

```
emotionless_options/
├── config/                 # Configuration files
│   ├── logging.yaml       # Logging configuration
│   └── settings.yaml      # Application settings
├── data/                  # Data storage
│   ├── raw/              # Raw scraped data
│   ├── processed/        # Processed data
│   └── models/           # Trained models
├── src/                   # Source code
│   ├── analysis/         # Analysis modules
│   │   ├── strategy_advisor.py
│   │   └── risk_metrics.py
│   ├── scrapers/         # Data scraping modules
│   │   ├── options_scraper.py
│   │   └── market_data.py
│   ├── sentiment/        # Sentiment analysis
│   │   ├── news_analyzer.py
│   │   └── social_analyzer.py
│   ├── utils/            # Utility functions
│   │   ├── validation.py
│   │   └── logging.py
│   └── examples/         # Example scripts
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
└── docs/                # Documentation
    ├── api/            # API documentation
    └── guides/         # User guides
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/emotionless_options.git
cd emotionless_options
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Basic options data retrieval:
```python
from emotionless_options.src.scrapers.options_scraper import OptionsScraper

scraper = OptionsScraper()
data = scraper.get_comprehensive_option_data(
    ticker="SPY",
    expiration="2025-05-27",
    strike=590.0,
    option_type="call"
)
```

2. Strategy recommendation:
```python
from emotionless_options.src.analysis.strategy_advisor import OptionStrategyAdvisor

advisor = OptionStrategyAdvisor()
recommendation = advisor.recommend_strategy(
    ticker="SPY",
    expiration="2025-05-27",
    strike=590.0,
    option_type="call"
)
```

## Configuration

The system can be configured through YAML files in the `config` directory:

- `logging.yaml`: Configure logging levels and formats
- `settings.yaml`: Configure application settings and parameters

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- yfinance for market data
- scipy for statistical calculations
- pandas for data manipulation 