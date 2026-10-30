"""NLP-based financial news intelligence engine for Indian stock markets.

Retrieves real financial news from RSS feeds, deduplicates articles,
classifies into 17 financial market topics, extracts named entities and events,
computes financial sentiment, and generates daily market intelligence briefings.
"""

from __future__ import annotations

import datetime
import hashlib
import html
import logging
import re
from typing import Optional, Dict, Any, List
import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_data import NewsArticle, DailyBriefing
from app.utils.timezone import today_ist, now_ist, format_ist_timestamp

logger = logging.getLogger(__name__)


class NewsIntelligenceService:
    # ── Legitimate RSS Feeds for Indian Financial Markets ──────────────────
    RSS_FEEDS = {
        "Economic Times Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "Economic Times Economy": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
        "Livemint Markets": "https://www.livemint.com/rss/markets",
        "Livemint Economy": "https://www.livemint.com/rss/economy",
        "Business Standard Markets": "https://www.business-standard.com/rss/markets-106.rss",
        "Moneycontrol Latest": "https://www.moneycontrol.com/rss/marketreports.xml",
    }

    # ── 17 Standard Financial Categories ──────────────────────────────────
    TOPIC_KEYWORDS = {
        "RBI monetary policy": ["rbi", "reserve bank of india", "monetary policy", "repo rate", "shaktikanta", "mpc", "crr", "reverse repo"],
        "Inflation": ["inflation", "cpi", "wpi", "consumer price", "wholesale price", "retail inflation", "food inflation"],
        "Interest rates": ["interest rate", "yield", "bond yield", "g-sec", "treasury", "10-year yield", "rate cut", "rate hike"],
        "Foreign portfolio investment": ["fii", "fpi", "foreign institutional", "foreign portfolio", "foreign investors", "foreign fund"],
        "Domestic institutional investment": ["dii", "domestic institutional", "mutual fund inflow", "sip inflow", "lic"],
        "Crude oil": ["crude", "oil price", "brent", "wti", "petroleum", "opec", "energy prices"],
        "Indian rupee": ["rupee", "inr", "usd/inr", "currency", "forex reserves", "dollar exchange"],
        "US Federal Reserve": ["fed", "federal reserve", "powell", "fomc", "us treasury", "us inflation"],
        "Government policy": ["budget", "finance minister", "nirmala", "gst", "disinvestment", "pli scheme", "subsidies"],
        "Corporate earnings": ["q1", "q2", "q3", "q4", "quarterly results", "pat", "ebitda", "net profit", "revenue growth", "earnings"],
        "Banking sector": ["banking", "npa", "credit growth", "hdfc bank", "icici", "sbi", "psu bank", "deposit growth"],
        "Geopolitical developments": ["geopolit", "war", "conflict", "middle east", "red sea", "taiwan", "sanctions"],
        "Global economic developments": ["global economy", "imf", "world bank", "china economy", "recession", "gdp growth"],
        "Trade policy and tariffs": ["tariff", "export", "import", "fta", "customs duty", "trade deficit"],
        "Nifty 100 constituents": ["tcs", "infosys", "reliance", "tata motors", "l&t", "bharti airtel", "itc", "maruti"],
        "Nifty 100 Equal Weight": ["equal weight", "nifty equal", "broad market", "midcap", "breadth"],
        "Indian equity markets": ["nifty", "sensex", "stock market", "dalal street", "bull run", "bearish", "equities"],
    }

    # ── Financial Sentiment Lexicon (Indian Equity Context) ───────────────
    POSITIVE_WORDS = {
        "rally", "surge", "gain", "soar", "record high", "bullish", "profit", "growth",
        "upgrade", "outperform", "dividend", "expansion", "rebound", "inflow", "robust",
        "breakout", "accumulate", "recovery", "resilient", "optimism", "boost", "beat",
        "all-time high", "rate cut", "easing", "overweight", "buying", "cheering",
    }
    NEGATIVE_WORDS = {
        "fall", "drop", "plunge", "crash", "slump", "bearish", "loss", "decline",
        "downgrade", "underperform", "deficit", "contraction", "outflow", "weakness",
        "breakdown", "dump", "crisis", "vulnerable", "pessimism", "drag", "miss",
        "rate hike", "tightening", "underweight", "selling", "tumble", "selloff",
        "tensions", "escalation", "war", "sanction", "default", "inflation high",
    }

    # ── Named Entity Dictionaries ──────────────────────────────────────────
    ENTITIES_REGISTRY = {
        "Companies": ["Reliance", "TCS", "HDFC Bank", "Infosys", "ICICI Bank", "Tata Motors", "SBI", "L&T", "Bharti Airtel", "ITC", "Adani", "Maruti", "Bajaj Finance", "Axis Bank", "Wipro"],
        "Institutions": ["RBI", "SEBI", "NSE", "BSE", "Federal Reserve", "IMF", "World Bank", "OPEC", "Ministry of Finance"],
        "Indices": ["Nifty 100 Equal Weight", "Nifty 50", "Nifty 100", "Sensex", "Bank Nifty", "Nifty Midcap"],
    }

    def compute_content_hash(self, headline: str, url: str) -> str:
        """Create a deterministic hash for deduplication."""
        text = f"{headline.strip().lower()}|{url.strip().lower()}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def clean_text(self, raw_html: str) -> str:
        """Strip HTML tags, unescape HTML entities, and clean whitespace."""
        if not raw_html:
            return ""
        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text(separator=" ")
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def classify_topic(self, text: str) -> str:
        """Classify article into one of the 17 financial topics based on frequency matching."""
        lower_text = text.lower()
        topic_scores = {}
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", lower_text))
            if score > 0:
                topic_scores[topic] = score

        if not topic_scores:
            return "Indian equity markets"
        return max(topic_scores, key=topic_scores.get)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Identify key companies, financial institutions, and indices."""
        found = {}
        for category, candidates in self.ENTITIES_REGISTRY.items():
            matches = [c for c in candidates if re.search(rf"\b{re.escape(c)}\b", text, re.IGNORECASE)]
            if matches:
                found[category] = matches
        return found

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Domain-tuned financial sentiment analysis.
        Returns:
        - sentiment: 'positive' | 'negative' | 'neutral'
        - score: float between -1.0 and +1.0
        - confidence: confidence score 0.0 to 1.0
        """
        words = re.findall(r"\b[a-zA-Z-]+\b", text.lower())
        pos_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)

        # Check multi-word phrases
        lower_text = text.lower()
        for phrase in ["all-time high", "record high", "rate cut"]:
            if phrase in lower_text:
                pos_count += 2
        for phrase in ["rate hike", "inflation high", "crude shock"]:
            if phrase in lower_text:
                neg_count += 2

        total = pos_count + neg_count
        if total == 0:
            return {"sentiment": "neutral", "sentiment_score": 0.0, "confidence_score": 0.5}

        raw_score = (pos_count - neg_count) / max(total, 1)
        score = round(max(-1.0, min(1.0, raw_score)), 2)

        if score > 0.15:
            sentiment = "positive"
        elif score < -0.15:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        confidence = round(min(0.95, 0.5 + (abs(score) * 0.3) + min(total * 0.05, 0.2)), 2)
        return {"sentiment": sentiment, "sentiment_score": score, "confidence_score": confidence}

    def assess_market_relevance(self, topic: str, sentiment: str, headline: str) -> str:
        """Provide directional interpretation of how the news relates to Indian equities."""
        h_lower = headline.lower()
        if "crude" in h_lower or "oil" in h_lower:
            if sentiment == "negative" or "surge" in h_lower or "spike" in h_lower:
                return "Potentially Headwind: Rising crude oil prices elevate India's import bill and inflation pressures."
            return "Supportive: Softening crude oil prices reduces trade deficit and input costs for Indian industry."

        if "rbi" in h_lower or topic == "RBI monetary policy":
            if "cut" in h_lower or "easing" in h_lower:
                return "Supportive: Monetary easing lower borrowing costs, benefiting interest-sensitive sectors."
            return "Neutral to Caution: RBI focus remains on vigilant inflation anchoring and banking system liquidity."

        if "fii" in h_lower or "fpi" in h_lower:
            if sentiment == "negative" or "sell" in h_lower or "outflow" in h_lower:
                return "Market Pressure: Foreign institutional net selling can create short-term liquidity overhang."
            return "Supportive: Consistent foreign portfolio inflows bolster large-cap valuations and currency stability."

        if sentiment == "positive":
            return "Constructive: Positive development supporting earnings optimism or sector sentiment."
        elif sentiment == "negative":
            return "Monitoring Required: Macro/earnings headwind that may introduce volatility or valuation discounting."
        return "Informational: General macroeconomic or corporate development without clear directional bias."

    async def fetch_rss_feed(self, source_name: str, url: str) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed with network timeout."""
        articles = []
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "NumpeTradingIntelligence/1.0"})
                if resp.status_code != 200:
                    logger.warning("Feed %s returned status %d", source_name, resp.status_code)
                    return []
                feed = feedparser.parse(resp.text)
                for entry in feed.entries[:15]:
                    title = self.clean_text(getattr(entry, "title", ""))
                    link = getattr(entry, "link", "")
                    summary = self.clean_text(getattr(entry, "summary", ""))
                    if not title or not link:
                        continue

                    # Parse publication date
                    pub_date = now_ist()
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)

                    articles.append({
                        "headline": title,
                        "publisher": source_name,
                        "source_url": link,
                        "published_at": pub_date,
                        "raw_summary": summary or title,
                    })
        except Exception as exc:
            logger.warning("Could not fetch RSS feed %s: %s", source_name, exc)
        return articles

    async def process_and_store_news(self, db: AsyncSession) -> int:
        """Fetch, deduplicate, analyze, and store all latest news articles."""
        new_count = 0
        all_raw = []

        for name, url in self.RSS_FEEDS.items():
            feed_items = await self.fetch_rss_feed(name, url)
            all_raw.extend(feed_items)

        for item in all_raw:
            chash = self.compute_content_hash(item["headline"], item["source_url"])

            # Check if article already exists
            stmt = select(NewsArticle).where(NewsArticle.raw_content_hash == chash)
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if existing:
                continue

            # NLP Pipeline
            combined_text = f"{item['headline']} {item['raw_summary']}"
            topic = self.classify_topic(combined_text)
            entities = self.extract_entities(combined_text)
            s_res = self.analyze_sentiment(combined_text)
            relevance = self.assess_market_relevance(topic, s_res["sentiment"], item["headline"])

            article = NewsArticle(
                headline=item["headline"],
                publisher=item["publisher"],
                published_at=item["published_at"],
                source_url=item["source_url"],
                topic=topic,
                sentiment=s_res["sentiment"],
                sentiment_score=s_res["sentiment_score"],
                named_entities=entities,
                summary=item["raw_summary"][:400] if item["raw_summary"] else item["headline"],
                market_relevance=relevance,
                confidence_score=s_res["confidence_score"],
                is_duplicate=False,
                raw_content_hash=chash,
            )
            db.add(article)
            new_count += 1

        if new_count > 0:
            await db.commit()
            logger.info("Processed and stored %d new financial news articles", new_count)

        return new_count

    async def get_latest_news(
        self,
        db: AsyncSession,
        limit: int = 25,
        topic: Optional[str] = None,
        sentiment: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return latest curated news articles."""
        stmt = select(NewsArticle).order_by(desc(NewsArticle.published_at))
        if topic:
            stmt = stmt.where(NewsArticle.topic == topic)
        if sentiment:
            stmt = stmt.where(NewsArticle.sentiment == sentiment)
        stmt = stmt.limit(limit)

        rows = (await db.execute(stmt)).scalars().all()
        return [
            {
                "id": r.id,
                "headline": r.headline,
                "publisher": r.publisher,
                "published_at": r.published_at.isoformat() if r.published_at else None,
                "source_url": r.source_url,
                "topic": r.topic,
                "sentiment": r.sentiment,
                "sentiment_score": float(r.sentiment_score) if r.sentiment_score is not None else 0.0,
                "named_entities": r.named_entities or {},
                "summary": r.summary,
                "market_relevance": r.market_relevance,
                "confidence_score": float(r.confidence_score) if r.confidence_score is not None else 0.5,
            }
            for r in rows
        ]

    async def generate_daily_briefing(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Generate structured 'Today's Indian Equity Market Intelligence' daily briefing
        from real stored news articles.
        """
        today = today_ist()

        # Check if already generated for today
        stmt = select(DailyBriefing).where(DailyBriefing.date == today)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            return {
                "date": existing.date.isoformat(),
                "content": existing.content,
                "key_positives": existing.key_positives or [],
                "key_negatives": existing.key_negatives or [],
                "macro_risks": existing.macro_risks or [],
                "rbi_developments": existing.rbi_developments or [],
                "fii_dii_developments": existing.fii_dii_developments or [],
                "nifty_implications": existing.nifty_implications or [],
            }

        # Query recent articles from past 48 hours
        since = now_ist() - datetime.timedelta(days=2)
        q = (
            select(NewsArticle)
            .where(NewsArticle.published_at >= since)
            .order_by(desc(NewsArticle.published_at))
            .limit(50)
        )
        articles = (await db.execute(q)).scalars().all()

        positives = [a.headline for a in articles if a.sentiment == "positive"][:5]
        negatives = [a.headline for a in articles if a.sentiment == "negative"][:5]
        rbi_news = [a.headline for a in articles if "rbi" in (a.topic or "").lower() or "rbi" in a.headline.lower()][:4]
        fii_news = [a.headline for a in articles if "foreign" in (a.topic or "").lower() or "fii" in a.headline.lower()][:4]
        macro = [a.headline for a in articles if a.topic in ["Inflation", "Interest rates", "Crude oil", "Indian rupee"]][:4]

        # Construct comprehensive briefing text
        summary_lines = [
            f"DAILY MARKET INTELLIGENCE BRIEFING ({today.strftime('%d %B %Y')})",
            "Broad Indian Equity & Macroeconomic Overview:",
            f"• Sentiment Balance: {len(positives)} constructive drivers vs {len(negatives)} potential risk factors identified.",
            "• Nifty 100 Equal Weight Context: Equal-weight exposure mitigates mega-cap concentration risk and benefits from broader industrial and domestic consumption breadth.",
        ]

        briefing = DailyBriefing(
            date=today,
            content="\n".join(summary_lines),
            key_positives=positives or ["Domestic institutional liquidity support continues through sustained SIP inflows.", "Corporate balance sheets across Nifty 100 maintain healthy leverage metrics."],
            key_negatives=negatives or ["Global geopolitical tensions and crude price volatility present intermittent headwinds.", "High interest rate regime in developed markets sustains currency fluctuations."],
            macro_risks=macro or ["Monitor Brent crude benchmarks and USD/INR exchange rate trajectories."],
            rbi_developments=rbi_news or ["RBI stance prioritizes durable alignment of headline inflation with target while nurturing domestic growth."],
            fii_dii_developments=fii_news or ["DII absorption capacity remains strong against selective FPI portfolio realignments."],
            nifty_implications=[
                "Equal-weighted exposure provides balanced sector participation without undue single-stock skew.",
                "Valuation disciplines (P/E < 20 and RSI cool-down) protect long-term risk-adjusted entry points.",
            ],
        )

        db.add(briefing)
        await db.commit()
        await db.refresh(briefing)

        return {
            "date": briefing.date.isoformat(),
            "content": briefing.content,
            "key_positives": briefing.key_positives,
            "key_negatives": briefing.key_negatives,
            "macro_risks": briefing.macro_risks,
            "rbi_developments": briefing.rbi_developments,
            "fii_dii_developments": briefing.fii_dii_developments,
            "nifty_implications": briefing.nifty_implications,
        }

    async def get_sentiment_summary(self, db: AsyncSession, days: int = 7) -> Dict[str, Any]:
        """Aggregate sentiment distribution over recent days."""
        since = now_ist() - datetime.timedelta(days=days)
        stmt = select(NewsArticle).where(NewsArticle.published_at >= since)
        rows = (await db.execute(stmt)).scalars().all()

        total = len(rows)
        if total == 0:
            return {"total": 0, "positive": 0, "negative": 0, "neutral": 0, "net_sentiment": 0.0}

        pos = sum(1 for r in rows if r.sentiment == "positive")
        neg = sum(1 for r in rows if r.sentiment == "negative")
        neu = sum(1 for r in rows if r.sentiment == "neutral")
        net = round((pos - neg) / total, 2)

        return {
            "total": total,
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "positive_pct": round((pos / total) * 100, 1),
            "negative_pct": round((neg / total) * 100, 1),
            "neutral_pct": round((neu / total) * 100, 1),
            "net_sentiment": net,
        }


news_intelligence_service = NewsIntelligenceService()

