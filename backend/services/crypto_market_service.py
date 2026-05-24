"""
FINEX - Crypto Market Service
Primary: Binance (unlimited, fastest)
Images: CoinGecko (cached 1hr, rate limited)
"""
import httpx
import asyncio
import time
from typing import Dict, List

BINANCE_BASE   = "https://api.binance.com/api/v3"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

CRYPTO_SYMBOLS = [
    {"symbol":"BTCUSDT",   "name":"Bitcoin",           "short":"BTC"},
    {"symbol":"ETHUSDT",   "name":"Ethereum",          "short":"ETH"},
    {"symbol":"BNBUSDT",   "name":"BNB",               "short":"BNB"},
    {"symbol":"SOLUSDT",   "name":"Solana",            "short":"SOL"},
    {"symbol":"XRPUSDT",   "name":"XRP",               "short":"XRP"},
    {"symbol":"ADAUSDT",   "name":"Cardano",           "short":"ADA"},
    {"symbol":"DOGEUSDT",  "name":"Dogecoin",          "short":"DOGE"},
    {"symbol":"DOTUSDT",   "name":"Polkadot",          "short":"DOT"},
    {"symbol":"MATICUSDT", "name":"Polygon",           "short":"MATIC"},
    {"symbol":"LTCUSDT",   "name":"Litecoin",          "short":"LTC"},
    {"symbol":"AVAXUSDT",  "name":"Avalanche",         "short":"AVAX"},
    {"symbol":"LINKUSDT",  "name":"Chainlink",         "short":"LINK"},
    {"symbol":"UNIUSDT",   "name":"Uniswap",           "short":"UNI"},
    {"symbol":"ATOMUSDT",  "name":"Cosmos",            "short":"ATOM"},
    {"symbol":"ETCUSDT",   "name":"Ethereum Classic",  "short":"ETC"},
    {"symbol":"XLMUSDT",   "name":"Stellar",           "short":"XLM"},
    {"symbol":"TRXUSDT",   "name":"TRON",              "short":"TRX"},
    {"symbol":"NEARUSDT",  "name":"NEAR Protocol",     "short":"NEAR"},
    {"symbol":"APTUSDT",   "name":"Aptos",             "short":"APT"},
    {"symbol":"ARBUSDT",   "name":"Arbitrum",          "short":"ARB"},
    {"symbol":"OPUSDT",    "name":"Optimism",          "short":"OP"},
    {"symbol":"SUIUSDT",   "name":"Sui",               "short":"SUI"},
    {"symbol":"SHIBUSDT",  "name":"Shiba Inu",         "short":"SHIB"},
    {"symbol":"INJUSDT",   "name":"Injective",         "short":"INJ"},
    {"symbol":"AAVEUSDT",  "name":"Aave",              "short":"AAVE"},
    {"symbol":"MKRUSDT",   "name":"Maker",             "short":"MKR"},
    {"symbol":"RUNEUSDT",  "name":"THORChain",         "short":"RUNE"},
    {"symbol":"FILUSDT",   "name":"Filecoin",          "short":"FIL"},
    {"symbol":"ICPUSDT",   "name":"Internet Computer", "short":"ICP"},
    {"symbol":"VETUSDT",   "name":"VeChain",           "short":"VET"},
    {"symbol":"GRTUSDT",   "name":"The Graph",         "short":"GRT"},
    {"symbol":"ALGOUSDT",  "name":"Algorand",          "short":"ALGO"},
    {"symbol":"EGLDUSDT",  "name":"MultiversX",        "short":"EGLD"},
    {"symbol":"XTZUSDT",   "name":"Tezos",             "short":"XTZ"},
    {"symbol":"EOSUSDT",   "name":"EOS",               "short":"EOS"},
    {"symbol":"APTUSDT",   "name":"Aptos",             "short":"APT"},
    {"symbol":"FTMUSDT",   "name":"Fantom",            "short":"FTM"},
    {"symbol":"SANDUSDT",  "name":"The Sandbox",       "short":"SAND"},
    {"symbol":"MANAUSDT",  "name":"Decentraland",      "short":"MANA"},
    {"symbol":"AXSUSDT",   "name":"Axie Infinity",     "short":"AXS"},
    {"symbol":"THETAUSDT", "name":"Theta Network",     "short":"THETA"},
    {"symbol":"KLAYUSDT",  "name":"Klaytn",            "short":"KLAY"},
    {"symbol":"HBARUSDT",  "name":"Hedera",            "short":"HBAR"},
    {"symbol":"FLOWUSDT",  "name":"Flow",              "short":"FLOW"},
    {"symbol":"CHZUSDT",   "name":"Chiliz",            "short":"CHZ"},
    {"symbol":"APEUSDT",   "name":"ApeCoin",           "short":"APE"},
    {"symbol":"GALAUSDT",  "name":"Gala",              "short":"GALA"},
    {"symbol":"ENJUSDT",   "name":"Enjin Coin",        "short":"ENJ"},
    {"symbol":"CRVUSDT",   "name":"Curve DAO",         "short":"CRV"},
    {"symbol":"SNXUSDT",   "name":"Synthetix",         "short":"SNX"},
    {"symbol":"COMPUSDT",  "name":"Compound",          "short":"COMP"},
    {"symbol":"YFIUSDT",   "name":"yearn.finance",     "short":"YFI"},
    {"symbol":"SUSHIUSDT", "name":"SushiSwap",         "short":"SUSHI"},
    {"symbol":"1INCHUSDT", "name":"1inch",             "short":"1INCH"},
    {"symbol":"BATUSDT",   "name":"Basic Attention",   "short":"BAT"},
    {"symbol":"ZRXUSDT",   "name":"0x Protocol",       "short":"ZRX"},
    {"symbol":"LRCUSDT",   "name":"Loopring",          "short":"LRC"},
    {"symbol":"QNTUSDT",   "name":"Quant",             "short":"QNT"},
    {"symbol":"IOTAUSDT",  "name":"IOTA",              "short":"IOTA"},
    {"symbol":"ZILUSDT",   "name":"Zilliqa",           "short":"ZIL"},
    {"symbol":"ONTUSDT",   "name":"Ontology",          "short":"ONT"},
    {"symbol":"WAVESUSDT", "name":"Waves",             "short":"WAVES"},
    {"symbol":"DASHUSDT",  "name":"Dash",              "short":"DASH"},
    {"symbol":"ZECUSDT",   "name":"Zcash",             "short":"ZEC"},
    {"symbol":"XMRUSDT",   "name":"Monero",            "short":"XMR"},
    {"symbol":"NEOUSDT",   "name":"NEO",               "short":"NEO"},
    {"symbol":"KSMUSDT",   "name":"Kusama",            "short":"KSM"},
    {"symbol":"CELOUSDT",  "name":"Celo",              "short":"CELO"},
    {"symbol":"STXUSDT",   "name":"Stacks",            "short":"STX"},
    {"symbol":"MINAUSDT",  "name":"Mina Protocol",     "short":"MINA"},
    {"symbol":"ROSAUSDT",  "name":"Ronin",             "short":"RON"},
    {"symbol":"ACHUSDT",   "name":"Alchemy Pay",       "short":"ACH"},
    {"symbol":"ANKRUSDT",  "name":"Ankr",              "short":"ANKR"},
    {"symbol":"BTTCUSDT",  "name":"BitTorrent",        "short":"BTTC"},
    {"symbol":"CKBUSDT",   "name":"Nervos Network",    "short":"CKB"},
    {"symbol":"COTIUSDT",  "name":"COTI",              "short":"COTI"},
    {"symbol":"CTSIUSDT",  "name":"Cartesi",           "short":"CTSI"},
    {"symbol":"DGBUSDT",   "name":"DigiByte",          "short":"DGB"},
    {"symbol":"DUSKUSDT",  "name":"Dusk Network",      "short":"DUSK"},
    {"symbol":"FETUSDT",   "name":"Fetch.ai",          "short":"FET"},
    {"symbol":"FORTHUSDT", "name":"Ampleforth Gov",    "short":"FORTH"},
    {"symbol":"GLMRUSDT",  "name":"Moonbeam",          "short":"GLMR"},
    {"symbol":"GMTUSDT",   "name":"STEPN",             "short":"GMT"},
    {"symbol":"HIGHUSDT",  "name":"Highstreet",        "short":"HIGH"},
    {"symbol":"HOOKUSDT",  "name":"Hooked Protocol",   "short":"HOOK"},
    {"symbol":"IDUSDT",    "name":"Space ID",          "short":"ID"},
    {"symbol":"JASMYUSDT", "name":"JasmyCoin",         "short":"JASMY"},
    {"symbol":"JUPUSDT",   "name":"Jupiter",           "short":"JUP"},
    {"symbol":"LDOUSDT",   "name":"Lido DAO",          "short":"LDO"},
    {"symbol":"MAGICUSDT", "name":"Magic",             "short":"MAGIC"},
    {"symbol":"MASKUSDT",  "name":"Mask Network",      "short":"MASK"},
    {"symbol":"MAVUSDT",   "name":"Maverick Protocol", "short":"MAV"},
    {"symbol":"MBLUSDT",   "name":"MovieBloc",         "short":"MBL"},
    {"symbol":"MTLUSDT",   "name":"Metal DAO",         "short":"MTL"},
    {"symbol":"OCEANUSDT", "name":"Ocean Protocol",    "short":"OCEAN"},
    {"symbol":"ONGUSDT",   "name":"Ontology Gas",      "short":"ONG"},
    {"symbol":"OXTUSDT",   "name":"Orchid",            "short":"OXT"},
    {"symbol":"PENDLEUSDT","name":"Pendle",            "short":"PENDLE"},
    {"symbol":"PEOPLEUSDT","name":"ConstitutionDAO",   "short":"PEOPLE"},
    {"symbol":"PHAUSDT",   "name":"Phala Network",     "short":"PHA"},
    {"symbol":"POLYXUSDT", "name":"Polymesh",          "short":"POLYX"},
    {"symbol":"POWRUSDT",  "name":"Power Ledger",      "short":"POWR"},
    {"symbol":"PYTHUSDT",  "name":"Pyth Network",      "short":"PYTH"},
    {"symbol":"RDNTUSDT",  "name":"Radiant Capital",   "short":"RDNT"},
    {"symbol":"RNDRUSDT",  "name":"Render",            "short":"RNDR"},
    {"symbol":"RSRUSDT",   "name":"Reserve Rights",    "short":"RSR"},
    {"symbol":"SEIUSDT",   "name":"Sei",               "short":"SEI"},
    {"symbol":"SFPUSDT",   "name":"SafePal",           "short":"SFP"},
    {"symbol":"SKLUSDT",   "name":"SKALE",             "short":"SKL"},
    {"symbol":"SLPUSDT",   "name":"Smooth Love Potion","short":"SLP"},
    {"symbol":"SONICUSDT", "name":"Sonic",             "short":"SONIC"},
    {"symbol":"SPELLUSDT", "name":"Spell Token",       "short":"SPELL"},
    {"symbol":"STGUSDT",   "name":"Stargate Finance",  "short":"STG"},
    {"symbol":"STORJUSDT", "name":"Storj",             "short":"STORJ"},
    {"symbol":"SUNUSDT",   "name":"Sun Token",         "short":"SUN"},
    {"symbol":"SXPUSDT",   "name":"Solar",             "short":"SXP"},
    {"symbol":"TWTUSDT",   "name":"Trust Wallet",      "short":"TWT"},
    {"symbol":"UMAUSDT",   "name":"UMA",               "short":"UMA"},
    {"symbol":"USDCUSDT",  "name":"USD Coin",          "short":"USDC"},
    {"symbol":"USTCUSDT",  "name":"TerraClassicUSD",   "short":"USTC"},
    {"symbol":"WLDUSDT",   "name":"Worldcoin",         "short":"WLD"},
    {"symbol":"WOOUSDT",   "name":"WOO Network",       "short":"WOO"},
    {"symbol":"XAIUSDT",   "name":"Xai",               "short":"XAI"},
    {"symbol":"XECUSDT",   "name":"eCash",             "short":"XEC"},
    {"symbol":"YGGUSDT",   "name":"Yield Guild Games", "short":"YGG"},
    {"symbol":"ZKUSDT",    "name":"zkSync",            "short":"ZK"},
]

META_MAP = {c["symbol"]: c for c in CRYPTO_SYMBOLS}

# Image cache - fetch from CoinGecko once per hour
_image_cache: Dict[str, str] = {}
_image_cache_time: float = 0
_CG_CACHE_TTL = 3600
_cg_last_call: float = 0
_CG_MIN_INTERVAL = 2.5

async def _ensure_image_cache():
    global _image_cache, _image_cache_time, _cg_last_call
    if time.time() - _image_cache_time < _CG_CACHE_TTL and _image_cache:
        return
    try:
        now = time.time()
        wait = _CG_MIN_INTERVAL - (now - _cg_last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        _cg_last_call = time.time()
        cg_ids = list(set([
            "bitcoin","ethereum","binancecoin","solana","ripple","cardano","dogecoin",
            "polkadot","matic-network","litecoin","avalanche-2","chainlink","uniswap",
            "cosmos","ethereum-classic","stellar","tron","near","aptos","arbitrum",
            "optimism","sui","shiba-inu","injective-protocol","aave","maker","thorchain",
            "filecoin","internet-computer","vechain","the-graph","algorand","tezos",
            "fantom","the-sandbox","decentraland","axie-infinity","theta-network",
            "hedera-hashgraph","flow","chiliz","apecoin","gala","enjincoin","curve-dao-token",
            "synthetix-network-token","compound-governance-token","yearn-finance","sushi",
            "1inch","basic-attention-token","loopring","quant-network","iota","zilliqa",
            "neo","kusama","celo","stacks","ankr","fetch-ai","stepn","lido-dao",
            "mask-network","ocean-protocol","render-token","skale","storj","trust-wallet-token",
            "uma","usd-coin","worldcoin-wld","woo-network","yield-guild-games"
        ]))
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(
                f"{COINGECKO_BASE}/coins/markets",
                params={"vs_currency":"usd","ids":",".join(cg_ids[:50]),"per_page":50,"page":1,"sparkline":False}
            )
            if res.status_code == 200:
                for coin in res.json():
                    for sym, meta in META_MAP.items():
                        if coin.get("symbol","").upper() == meta["short"].upper():
                            _image_cache[sym] = coin.get("image","")
                _image_cache_time = time.time()
    except Exception:
        pass

async def get_all_crypto_tickers(page: int = 0, page_size: int = 10) -> List[Dict]:
    start = page * page_size
    batch = CRYPTO_SYMBOLS[start: start + page_size]
    if not batch:
        return []
    asyncio.create_task(_ensure_image_cache())
    try:
        symbols_str = '["' + '","'.join([c["symbol"] for c in batch]) + '"]'
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(f"{BINANCE_BASE}/ticker/24hr", params={"symbols": symbols_str})
            data = res.json()
            if isinstance(data, list):
                results = []
                for d in data:
                    sym = d.get("symbol")
                    meta = META_MAP.get(sym)
                    if not meta:
                        continue
                    results.append({
                        "symbol":         meta["short"],
                        "binance_symbol": sym,
                        "name":           meta["name"],
                        "price":          float(d.get("lastPrice", 0)),
                        "change":         float(d.get("priceChange", 0)),
                        "change_percent": float(d.get("priceChangePercent", 0)),
                        "high":           float(d.get("highPrice", 0)),
                        "low":           float(d.get("lowPrice", 0)),
                        "volume":         float(d.get("volume", 0)),
                        "quote_volume":   float(d.get("quoteVolume", 0)),
                        "open":           float(d.get("openPrice", 0)),
                        "market_cap":     0,
                        "image":          _image_cache.get(sym, ""),
                    })
                return results
    except Exception as e:
        print(f"Binance batch error: {e}")
    return await _binance_fallback(batch)

async def _binance_fallback(batch) -> List[Dict]:
    results = []
    for meta in batch:
        t = await get_crypto_ticker(meta["symbol"])
        if t:
            results.append(t)
    return results

async def get_crypto_ticker(symbol: str) -> Dict:
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get(f"{BINANCE_BASE}/ticker/24hr", params={"symbol": symbol})
            d = res.json()
            if "code" in d:
                return None
            meta = META_MAP.get(symbol, {"name": symbol, "short": symbol})
            return {
                "symbol":         meta["short"],
                "binance_symbol": symbol,
                "name":           meta["name"],
                "price":          float(d.get("lastPrice", 0)),
                "change":         float(d.get("priceChange", 0)),
                "change_percent": float(d.get("priceChangePercent", 0)),
                "high":           float(d.get("highPrice", 0)),
                "low":            float(d.get("lowPrice", 0)),
                "volume":         float(d.get("volume", 0)),
                "quote_volume":   float(d.get("quoteVolume", 0)),
                "open":           float(d.get("openPrice", 0)),
                "market_cap":     0,
                "image":          _image_cache.get(symbol, ""),
            }
    except Exception as e:
        print(f"Binance ticker error {symbol}: {e}")
        return None

async def get_crypto_klines(symbol: str, interval: str = "1d", limit: int = 60) -> List[Dict]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(f"{BINANCE_BASE}/klines", params={
                "symbol": symbol, "interval": interval, "limit": limit
            })
            data = res.json()
            if not isinstance(data, list):
                return []
            return [
                {
                    "time":   int(k[0]) // 1000,
                    "open":   float(k[1]),
                    "high":   float(k[2]),
                    "low":    float(k[3]),
                    "close":  float(k[4]),
                    "volume": float(k[5]),
                }
                for k in data
            ]
    except Exception as e:
        print(f"Binance klines error {symbol}: {e}")
        return []
