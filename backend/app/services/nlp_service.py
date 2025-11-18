"""
NLP Service - Vietnamese keyword extraction and sentiment analysis.
Uses underthesea for Vietnamese text processing.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

try:
    from underthesea import word_tokenize, pos_tag, sentiment
except ImportError:
    # underthesea not installed, NLP features disabled
    word_tokenize = None
    pos_tag = None
    sentiment = None


class NLPService:
    """Service for Vietnamese NLP operations."""

    def __init__(self):
        """Initialize NLP service."""
        self.stopwords = self._load_vietnamese_stopwords()

    def _load_vietnamese_stopwords(self) -> set:
        """Load Vietnamese stopwords list."""
        # Common Vietnamese stopwords
        return {
            "là", "của", "và", "có", "được", "này", "trong", "cho", "với", "những",
            "các", "được", "từ", "theo", "về", "đã", "sẽ", "để", "khi", "một",
            "không", "người", "năm", "như", "đến", "vào", "ra", "các", "việc",
            "cũng", "còn", "nhưng", "vẫn", "đang", "đều", "lại", "hay", "hoặc",
        }

    def extract_keywords(
        self, text: str, top_n: int = 50, min_word_length: int = 2
    ) -> List[Dict[str, Any]]:
        """Extract keywords from Vietnamese text using TF-IDF-like approach.
        
        Args:
            text: Vietnamese text to extract keywords from
            top_n: Number of top keywords to return
            min_word_length: Minimum word length to consider
            
        Returns:
            List of keywords with frequency and scores
        """
        if not word_tokenize or not pos_tag:
            # underthesea not available, returning empty keywords
            return []

        try:
            # Tokenize Vietnamese text
            tokens = word_tokenize(text.lower())
            
            # POS tagging to filter for nouns, verbs, adjectives
            pos_tags = pos_tag(text)
            
            # Filter words by POS tags (keep nouns, verbs, adjectives)
            filtered_words = [
                word for word, tag in pos_tags
                if tag in ("N", "V", "A", "Np")  # Noun, Verb, Adjective, Proper noun
                and word not in self.stopwords
                and len(word) >= min_word_length
                and not word.isdigit()
            ]
            
            # Count word frequencies
            word_counts = Counter(filtered_words)
            total_words = len(filtered_words)
            
            # Calculate normalized frequency
            keywords = []
            max_count = max(word_counts.values()) if word_counts else 1
            
            for word, count in word_counts.most_common(top_n):
                keywords.append({
                    "keyword": word,
                    "count": count,
                    "frequency": round(count / max_count, 3),
                    "tf_score": round(count / total_words, 4),
                })
            
            return keywords
            
        except Exception as e:
            print(f"❌ Keyword extraction failed: {str(e)}")
            return []

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of Vietnamese text.
        
        Args:
            text: Vietnamese text to analyze
            
        Returns:
            Dictionary with sentiment label and confidence
        """
        if not sentiment:
            # underthesea sentiment analysis not available
            return {"sentiment": "neutral", "confidence": 0.5}

        try:
            result = sentiment(text)
            
            # Map underthesea output to our format
            sentiment_map = {
                "positive": "positive",
                "negative": "negative",
                "neutral": "neutral",
            }
            
            return {
                "sentiment": sentiment_map.get(result, "neutral"),
                "confidence": 0.8,  # underthesea doesn't provide confidence
            }
            
        except Exception as e:
            # Sentiment analysis failed - fallback to neutral
            return {"sentiment": "neutral", "confidence": 0.5}

    def extract_keywords_with_sentiment(
        self, documents: List[str], top_n: int = 50
    ) -> List[Dict[str, Any]]:
        """Extract keywords from multiple documents with sentiment analysis.
        
        Args:
            documents: List of text documents
            top_n: Number of top keywords to return
            
        Returns:
            List of keywords with aggregated sentiment
        """
        # Combine all documents
        combined_text = " ".join(documents)
        
        # Extract keywords
        keywords = self.extract_keywords(combined_text, top_n=top_n)
        
        # Analyze sentiment for each document
        sentiments = [self.analyze_sentiment(doc) for doc in documents]
        
        # Aggregate sentiment
        sentiment_counts = Counter(s["sentiment"] for s in sentiments)
        dominant_sentiment = sentiment_counts.most_common(1)[0][0] if sentiment_counts else "neutral"
        
        # Add sentiment to keywords
        for kw in keywords:
            kw["sentiment"] = dominant_sentiment
        
        return keywords

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from Vietnamese text.
        
        Args:
            text: Vietnamese text
            
        Returns:
            List of entities with types (PERSON, ORG, LOC, etc.)
        """
        if not pos_tag:
            return []

        try:
            pos_tags = pos_tag(text)
            
            # Extract proper nouns as entities
            entities = []
            for word, tag in pos_tags:
                if tag == "Np":  # Proper noun
                    entities.append({
                        "text": word,
                        "type": "ENTITY",
                    })
            
            return entities
            
        except Exception as e:
            print(f"❌ Entity extraction failed: {str(e)}")
            return []

    def summarize_risk_keywords(
        self, news_summaries: List[str], top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """Extract risk-related keywords from news summaries.
        
        Args:
            news_summaries: List of news summary texts
            top_n: Number of keywords to return
            
        Returns:
            List of risk keywords with frequencies
        """
        # Risk-related terms to boost
        risk_terms = {
            "bão", "thiên tai", "tắc nghẽn", "giá", "tăng", "giảm", "delay",
            "cạnh tranh", "mất", "thị phần", "ngừng", "đình công", "khan hiếm",
            "thiếu hụt", "tồn kho", "lỗi", "recall", "thu hồi",
        }
        
        keywords = self.extract_keywords_with_sentiment(news_summaries, top_n=top_n * 2)
        
        # Boost risk-related keywords
        for kw in keywords:
            if any(term in kw["keyword"] for term in risk_terms):
                kw["frequency"] *= 1.5
                kw["risk_relevance"] = "high"
            else:
                kw["risk_relevance"] = "medium"
        
        # Re-sort by adjusted frequency
        keywords.sort(key=lambda x: x["frequency"], reverse=True)
        
        return keywords[:top_n]


# Global NLP service instance
nlp_service = NLPService()


def get_nlp_service() -> NLPService:
    """Get NLP service instance."""
    return nlp_service
