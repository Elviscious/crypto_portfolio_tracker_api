# Crypto Portfolio Tracker API 📊

A robust FastAPI-based cryptocurrency portfolio tracking API that provides real-time portfolio management and analysis using CoinGecko's market data.

## Features 🚀

### Real-Time Crypto Data Integration

- Live price updates from CoinGecko API
- Support for 100+ cryptocurrencies
- Automatic price updates during portfolio analysis
- Market data validation for accurate tracking

### Portfolio Management

- Create and track cryptocurrency trades
- Real-time profit/loss calculations
- Portfolio performance analytics
- Support for multiple users via User-ID system

### Supported Cryptocurrencies

- Major cryptocurrencies (BTC, ETH, etc.)
- DeFi tokens (AAVE, UNI, SUSHI, etc.)
- Layer 1 blockchains (SOL, ADA, etc.)
- Layer 2 solutions (MATIC, ARB, OP)
- Stablecoins (USDT, USDC, DAI)
- And many more!

### Advanced Calculations

- Unrealized profit/loss tracking
- Percentage change calculations
- Total portfolio value analysis
- Per-trade performance metrics

## API Endpoints 🛣️

### 1. Create Trade

```http
POST /trades
Header: User-ID: <your-user-id>
```

**Request Body:**

```json
{
	"coin_symbol": "BTC",
	"quantity": 0.5,
	"avg_buy_price": 30000.0
}
```

**Response:**

```json
{
	"message": "Trade created successfully",
	"trade_id": 1
}
```

### 2. Portfolio Analysis

```http
GET /portfolio/analysis
Header: User-ID: <your-user-id>
```

**Response:**

```json
{
	"total_portfolio_value": 50000.0,
	"total_profit_loss": 5000.0,
	"total_percent_change": 10.0,
	"trades_analysis": [
		{
			"coin_symbol": "BTC",
			"quantity": 0.5,
			"avg_buy_price": 30000.0,
			"current_price": 35000.0,
			"unrealized_pnl": 2500.0,
			"percent_change": 16.67
		}
		// ... other trades
	]
}
```

## Technical Features 🔧

### Error Handling

- Comprehensive error messages
- Input validation
- Database transaction management
- API error status codes

### Database Integration

- PostgreSQL database
- SQLAlchemy ORM
- Efficient database queries
- Transaction safety

### Security Features

- CORS support
- User-specific data isolation
- Input sanitization
- Error message sanitization

## Setup and Installation 🔌

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Required Packages

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pycoingecko
```

### Database Setup

1. Create PostgreSQL database named 'crypto_tracker_db'
2. Update DATABASE_URL in database.py if needed
3. Tables are automatically created on startup

### Running the API

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation 📚

Access the interactive API documentation at:

```
http://localhost:8000/docs
```

## Integration Examples 💻

### React Integration

```javascript
// Create a trade
const createTrade = async (tradeData) => {
	try {
		const response = await fetch("http://localhost:8000/trades", {
			method: "POST",
			headers: {
				"User-ID": "your-user-id",
				"Content-Type": "application/json",
			},
			body: JSON.stringify(tradeData),
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.detail || "Failed to create trade");
		}

		return await response.json();
	} catch (error) {
		console.error("Error creating trade:", error.message);
		throw error;
	}
};

// Get portfolio analysis
const getPortfolio = async () => {
	try {
		const response = await fetch("http://localhost:8000/portfolio/analysis", {
			method: "GET",
			headers: {
				"User-ID": "your-user-id",
			},
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.detail || "Failed to fetch portfolio");
		}

		return await response.json();
	} catch (error) {
		console.error("Error fetching portfolio:", error.message);
		throw error;
	}
};
```

````

## Features in Detail 🔍

### Price Calculation Logic
- Real-time price fetching from CoinGecko
- Quantity-aware price calculations
- Precise decimal arithmetic for financial calculations
- Fallback mechanisms for API disruptions

### Portfolio Analysis
- Individual trade performance tracking
- Aggregate portfolio metrics
- Real-time price updates during analysis
- Historical price comparison

### Data Validation
- Cryptocurrency symbol validation
- Quantity and price validation
- User input sanitization
- Database constraint validation

## Best Practices 👌

1. Always provide a valid User-ID header
2. Handle API errors in your frontend
3. Implement proper error handling for network issues
4. Cache responses when appropriate
5. Implement rate limiting in production

## Error Handling Examples ⚠️

```javascript
// Example error responses
{
    "detail": "User-ID header missing"
}

{
    "detail": "Invalid coin symbol: XYZ. This symbol was not found on CoinGecko."
}

{
    "detail": "No trades found for this user"
}
````

## Contributing 🤝

Feel free to submit issues and enhancement requests!
