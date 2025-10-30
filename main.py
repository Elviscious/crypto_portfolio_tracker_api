from contextlib import asynccontextmanager
from database import Trade, create_tables, get_db
from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from pycoingecko import CoinGeckoAPI
from typing import Dict, Optional
import asyncio


class TradeCreate(BaseModel):
    coin_symbol: str = Field(..., example="BTC")
    quantity: float = Field(..., gt=0, example=0.5)
    avg_buy_price: float = Field(..., gt=0, example=30000.0)


class TradeAnalysisItem(BaseModel):
    coin_symbol: str
    quantity: float
    avg_buy_price: float
    current_price: float
    unrealized_pnl: float
    percent_change: float


class PortfolioAnalysisResponse(BaseModel):
    total_portfolio_value: float
    total_profit_loss: float
    total_percent_change: float
    trades_analysis: list[TradeAnalysisItem]


class TradeResponse(BaseModel):
    message: str
    trade_id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables at startup
    create_tables()
    print("Database tables created.")
    yield
    print("Shutting down...")
    # No specific shutdown actions needed

# Initialize CoinGecko client
cg = CoinGeckoAPI()

# Cache for coin IDs to avoid repeated API calls
coin_id_cache: Dict[str, str] = {}


async def get_coin_id(symbol: str) -> Optional[str]:
    """Get CoinGecko coin ID from symbol"""
    if symbol.lower() in coin_id_cache:
        return coin_id_cache[symbol.lower()]

    try:
        # Get list of coins sorted by market cap
        coins_list = cg.get_coins_markets(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=250,  # Get top coins by market cap
            sparkline=False
        )

        # Priority matching for major coins
        major_coins = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'usdt': 'tether',
            'usdc': 'usd-coin',
            'bnb': 'binancecoin',
            'xrp': 'ripple',
            'sol': 'solana',
            'ada': 'cardano',
            'doge': 'dogecoin',
            'trx': 'tron',
            'dot': 'polkadot',
            'matic': 'matic-network',
            'dai': 'dai',
            'ltc': 'litecoin',
            'shib': 'shiba-inu',
            'avax': 'avalanche-2',
            'uni': 'uniswap',
            'link': 'chainlink',
            'atom': 'cosmos',
            'xlm': 'stellar',
            'near': 'near',
            'algo': 'algorand',
            'icp': 'internet-computer',
            'vet': 'vechain',
            'fil': 'filecoin',
            'aave': 'aave',
            'sand': 'the-sandbox',
            'mana': 'decentraland',
            'grt': 'the-graph',
            'axs': 'axie-infinity',
            'neo': 'neo',
            'mkr': 'maker',
            'egld': 'elrond-erd-2',
            'theta': 'theta-token',
            'ftm': 'fantom',
            'xtz': 'tezos',
            'flow': 'flow',
            'kcs': 'kucoin-shares',
            'hbar': 'hedera-hashgraph',
            'eos': 'eos',
            'cake': 'pancakeswap-token',
            'xmr': 'monero',
            'rune': 'thorchain',
            'waves': 'waves',
            'qdx': 'quidax',
            'comp': 'compound-governance-token',
            'zec': 'zcash',
            'enj': 'enjincoin',
            'dash': 'dash',
            'celo': 'celo',
            # Adding more major tokens
            'apt': 'aptos',
            'arb': 'arbitrum',
            'op': 'optimism',
            'sui': 'sui',
            'inj': 'injective-protocol',
            'blur': 'blur',
            'pepe': 'pepe',
            'sei': 'sei-network',
            'stx': 'blockstack',
            'cfx': 'conflux-token',
            'kava': 'kava',
            'gala': 'gala',
            'rndr': 'render-token',
            'ldo': 'lido-dao',
            'imx': 'immutable-x',
            '1inch': '1inch',
            'ant': 'aragon',
            'api3': 'api3',
            'ar': 'arweave',
            'audio': 'audius',
            'bal': 'balancer',
            'band': 'band-protocol',
            'bat': 'basic-attention-token',
            'btt': 'bittorrent',
            'cel': 'celsius-degree-token',
            'chz': 'chiliz',
            'crv': 'curve-dao-token',
            'cvc': 'civic',
            'dag': 'constellation-labs',
            'dent': 'dent',
            'dydx': 'dydx',
            'eng': 'engine',
            'fet': 'fetch-ai',
            'ftt': 'ftx-token',
            'glm': 'golem',
            'gmx': 'gmx',
            'gtc': 'gitcoin',
            'hnt': 'helium',
            'hot': 'holotoken',
            'ilv': 'illuvium',
            'jasmy': 'jasmycoin',
            'knc': 'kyber-network-crystal',
            'lrc': 'loopring',
            'mask': 'mask-network',
            'mina': 'mina-protocol',
            'ocean': 'ocean-protocol',
            'omg': 'omisego',
            'perp': 'perpetual-protocol',
            'qnt': 'quant-network',
            'ren': 'republic-protocol',
            'rlc': 'iexec-rlc',
            'rose': 'oasis-network',
            'rsr': 'reserve-rights-token',
            'sfp': 'safepal',
            'skl': 'skale',
            'snx': 'havven',
            'storj': 'storj',
            'sushi': 'sushi',
            'syn': 'synapse-2',
            'sys': 'syscoin',
            'tlm': 'alien-worlds',
            'torn': 'tornado-cash',
            'tribe': 'tribe-2',
            'tusd': 'true-usd',
            'uma': 'uma',
            'unfi': 'unifi-protocol-dao',
            'wtc': 'waltonchain',
            'xvg': 'verge',
            'yfi': 'yearn-finance',
            'ygg': 'yield-guild-games',
            'zil': 'zilliqa',
            'zrx': '0x'
        }

        # Check if it's a major coin first
        if symbol.lower() in major_coins:
            coin_id = major_coins[symbol.lower()]
            coin_id_cache[symbol.lower()] = coin_id
            print(f"Debug - Matched major coin: {symbol.upper()} -> {coin_id}")
            return coin_id

        # If not a major coin, find in the market cap sorted list
        for coin in coins_list:
            if coin['symbol'].lower() == symbol.lower():
                coin_id_cache[symbol.lower()] = coin['id']
                print(
                    f"Debug - Matched coin by market cap: {symbol.upper()} -> {coin['id']}")
                return coin['id']

        # If still not found, try the full coins list as fallback
        full_coins_list = cg.get_coins_list()
        for coin in full_coins_list:
            if coin['symbol'].lower() == symbol.lower():
                coin_id_cache[symbol.lower()] = coin['id']
                print(
                    f"Debug - Matched coin from full list: {symbol.upper()} -> {coin['id']}")
                return coin['id']

        print(f"Debug - No match found for symbol: {symbol.upper()}")
        return None

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching coin data from CoinGecko: {str(e)}"
        )


async def get_current_price(coin_id: str, quantity: float = 1.0) -> float:
    """
    Get current price for a coin from CoinGecko
    Parameters:
        coin_id: The CoinGecko ID of the coin
        quantity: The quantity of the coin (default is 1.0 for single unit price)
    Returns:
        The current price for the specified quantity
    """
    try:
        # Get detailed market data for accurate pricing
        coin_data = cg.get_coins_markets(
            vs_currency='usd',
            ids=[coin_id],
            order='market_cap_desc',
            per_page=1,
            page=1,
            sparkline=False
        )

        if not coin_data or len(coin_data) == 0:
            raise Exception(f"No price data found for coin {coin_id}")

        unit_price = float(coin_data[0]['current_price'])
        total_price = unit_price * quantity

        return unit_price  # Return unit price, calculations will be done in the trade functions

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching price data from CoinGecko: {str(e)}"
        )

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/trades", response_model=TradeResponse)
async def create_trade(trade: TradeCreate, user_id: str = Header(alias="User-ID"), db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID header missing")

    try:
        # Validate coin symbol against CoinGecko API
        coin_id = await get_coin_id(trade.coin_symbol)
        if not coin_id:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid coin symbol: {trade.coin_symbol}. This symbol was not found on CoinGecko."
            )

        # Get current price from CoinGecko with quantity
        unit_price = await get_current_price(coin_id, trade.quantity)

        # Calculate initial PnL and percent change with precise decimal arithmetic
        initial_investment = trade.quantity * trade.avg_buy_price
        current_value = trade.quantity * unit_price
        unrealized_pnl = current_value - initial_investment

        # Calculate percent change, handling division by zero
        if initial_investment > 0:
            percent_change = (unrealized_pnl / initial_investment) * 100
        else:
            percent_change = 0.0

        new_trade = Trade(
            user_id=user_id,
            coin_symbol=trade.coin_symbol.upper(),
            quantity=trade.quantity,
            avg_buy_price=trade.avg_buy_price,
            current_price=unit_price,
            unrealized_pnl=unrealized_pnl,
            percent_change=percent_change
        )

        db.add(new_trade)
        db.commit()
        db.refresh(new_trade)

        return {"message": "Trade created successfully", "trade_id": new_trade.id}

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the trade: {str(e)}"
        )


@app.get("/portfolio/analysis", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(user_id: str = Header(alias="User-ID"), db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID header missing")

    try:
        trades = db.query(Trade).filter(Trade.user_id == user_id).all()

        if not trades:
            raise HTTPException(
                status_code=404, detail="No trades found for this user")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching trades: {str(e)}"
        )

    total_portfolio_value = 0.0
    total_profit_loss = 0.0
    trades_analysis = []

    for trade in trades:
        try:
            # Get current price from CoinGecko
            coin_id = await get_coin_id(trade.coin_symbol)
            if coin_id:
                current_price = await get_current_price(coin_id)

                # Update trade's current price in database
                trade.current_price = current_price

                # Calculate values with precise arithmetic
                initial_investment = trade.quantity * trade.avg_buy_price
                current_value = trade.quantity * current_price
                unrealized_pnl = current_value - initial_investment

                # Calculate percent change, handling division by zero
                if initial_investment > 0:
                    percent_change = (
                        unrealized_pnl / initial_investment) * 100
                else:
                    percent_change = 0.0

                print(f"\nDebug - Portfolio Analysis for {trade.coin_symbol}:")
                print(f"Quantity: {trade.quantity}")
                print(f"Avg Buy Price: ${trade.avg_buy_price:,.2f}")
                print(f"Current Price: ${current_price:,.2f}")
                print(f"Initial Investment: ${initial_investment:,.2f}")
                print(f"Current Value: ${current_value:,.2f}")
                print(f"Unrealized PnL: ${unrealized_pnl:,.2f}")
                print(f"Percent Change: {percent_change:.2f}%")

                total_portfolio_value += current_value
                total_profit_loss += unrealized_pnl

                # Update the trade in the database with new values
                trade.unrealized_pnl = unrealized_pnl
                trade.percent_change = percent_change
                db.add(trade)

                trades_analysis.append(
                    TradeAnalysisItem(
                        coin_symbol=trade.coin_symbol,
                        quantity=trade.quantity,
                        avg_buy_price=trade.avg_buy_price,
                        current_price=current_price,
                        unrealized_pnl=unrealized_pnl,
                        percent_change=percent_change
                    )
                )
        except Exception as e:
            # If we can't get current price, use the stored price
            current_price = trade.current_price
            total_value = trade.quantity * current_price
            unrealized_pnl = (
                current_price - trade.avg_buy_price) * trade.quantity
            percent_change = (
                (current_price - trade.avg_buy_price) / trade.avg_buy_price) * 100

            total_portfolio_value += total_value
            total_profit_loss += unrealized_pnl
            trades_analysis.append(
                TradeAnalysisItem(
                    coin_symbol=trade.coin_symbol,
                    quantity=trade.quantity,
                    avg_buy_price=trade.avg_buy_price,
                    current_price=current_price,
                    unrealized_pnl=unrealized_pnl,
                    percent_change=percent_change
                )
            )
    # Calculate total percent change based on total investment and current value
    total_investment = sum(
        trade.quantity * trade.avg_buy_price for trade in trades)
    if total_investment > 0:
        total_percent_change = (total_profit_loss / total_investment) * 100
    else:
        total_percent_change = 0.0

    # Commit the updates to the database
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating trade values: {str(e)}")

    return PortfolioAnalysisResponse(
        total_portfolio_value=total_portfolio_value,
        total_profit_loss=total_profit_loss,
        total_percent_change=total_percent_change,
        trades_analysis=trades_analysis
    )
