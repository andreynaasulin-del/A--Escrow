"""
AI Service for parsing deal data using OpenAI GPT-4o.
Handles natural language to structured JSON conversion.
[AUDIT FIX] Added retry logic with tenacity
"""

import json
import logging
from html import escape
from typing import Optional
from dataclasses import dataclass
from openai import AsyncOpenAI, RateLimitError, APIError

# [AUDIT FIX] Import tenacity for retry logic
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

from prompts import DEAL_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class ParsedDeal:
    """Structured deal data extracted by AI."""
    seller_username: Optional[str]
    buyer_username: Optional[str]
    amount: Optional[float]
    currency: Optional[str]
    item_description: Optional[str]
    deadline_hours: Optional[int]
    parse_confidence: str  # high, medium, low
    missing_fields: list[str]
    raw_json: dict
    
    @property
    def is_valid(self) -> bool:
        """Check if deal has minimum required fields."""
        return all([
            self.amount is not None,
            self.currency is not None,
            self.item_description is not None,
        ])
    
    @property
    def has_both_parties(self) -> bool:
        """Check if both seller and buyer are specified."""
        return self.seller_username is not None and self.buyer_username is not None
    
    def to_display_card(self) -> str:
        """Format deal as a visual card for Telegram."""
        lines = ["🔐 <b>Deal Card</b>", "─" * 20]
        
        if self.item_description:
            lines.append(f"📦 <b>Item:</b> {self.item_description}")
        if self.amount and self.currency:
            lines.append(f"💰 <b>Amount:</b> {self.amount} {self.currency}")
        if self.seller_username:
            lines.append(f"🏪 <b>Seller:</b> {self.seller_username}")
        if self.buyer_username:
            lines.append(f"🛒 <b>Buyer:</b> {self.buyer_username}")
        if self.deadline_hours:
            lines.append(f"⏰ <b>Deadline:</b> {self.deadline_hours} hours")
        
        lines.append("─" * 20)
        
        # Confidence indicator
        conf_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(self.parse_confidence, "⚪")
        lines.append(f"{conf_emoji} Parse confidence: {self.parse_confidence}")
        
        if self.missing_fields:
            lines.append(f"⚠️ Missing: {', '.join(self.missing_fields)}")
        
        return "\n".join(lines)


class AIService:
    """Service for AI-powered deal parsing using OpenAI GPT-4o."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"🤖 AI Service initialized with model: {model}")
    
    async def _call_openai(self, user_text: str) -> str:
        """
        [AUDIT FIX] Separated API call for retry decorator.
        Makes the actual OpenAI API request.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": DEAL_EXTRACTION_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Deal description: {user_text}"
                }
            ],
            temperature=0.1,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content.strip()
    
    async def parse_deal(self, user_text: str) -> ParsedDeal:
        """
        Parse natural language deal description into structured data.
        [AUDIT FIX] Added retry logic for API resilience.
        
        Args:
            user_text: Raw user input describing the deal
            
        Returns:
            ParsedDeal object with extracted data
            
        Raises:
            ValueError: If AI response cannot be parsed as JSON
        """
        logger.info(f"🔍 Parsing deal text: {user_text[:50]}...")
        
        # [AUDIT FIX] Retry logic with exponential backoff
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response_text = await self._call_openai(user_text)
                logger.debug(f"AI response: {response_text}")
                
                # Parse JSON
                data = json.loads(response_text)
                
                # [SECURITY] Escape HTML in user-provided strings to prevent XSS
                item_desc = data.get("item_description")
                if item_desc:
                    item_desc = escape(item_desc)

                parsed = ParsedDeal(
                    seller_username=data.get("seller_username"),
                    buyer_username=data.get("buyer_username"),
                    amount=data.get("amount"),
                    currency=data.get("currency"),
                    item_description=item_desc,
                    deadline_hours=data.get("deadline_hours"),
                    parse_confidence=data.get("parse_confidence", "low"),
                    missing_fields=data.get("missing_fields", []),
                    raw_json=data,
                )
                
                logger.info(f"✅ Deal parsed successfully. Confidence: {parsed.parse_confidence}")
                return parsed
                
            except RateLimitError as e:
                # [AUDIT FIX] Specific handling for rate limits
                last_error = e
                wait_time = 2 ** (attempt + 1)  # Exponential backoff: 2, 4, 8 seconds
                logger.warning(f"⚠️ Rate limit hit, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                import asyncio
                await asyncio.sleep(wait_time)
                
            except APIError as e:
                # [AUDIT FIX] Handle API errors with retry
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"⚠️ API error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries}): {e}")
                    import asyncio
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ API error after {max_retries} attempts: {e}")
                    raise ValueError(f"AI service temporarily unavailable. Please try again later.")
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse AI response as JSON: {e}")
                raise ValueError("AI response was not valid JSON. Please try again with clearer description.")
            
            except Exception as e:
                logger.error(f"❌ AI service error: {e}")
                raise ValueError(f"AI service error: {str(e)}")
        
        # If we exhausted all retries
        if last_error:
            logger.error(f"❌ All {max_retries} retries failed: {last_error}")
            raise ValueError("AI service is busy. Please try again in a few seconds.")
    
    async def health_check(self) -> bool:
        """Check if AI service is operational."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'OK' if you're working."}],
                max_tokens=10
            )
            return "OK" in response.choices[0].message.content.upper()
        except Exception as e:
            logger.error(f"❌ AI health check failed: {e}")
            return False
