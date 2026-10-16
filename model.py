from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ItemReport(BaseModel):
    item_id: Optional[str] = None
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=5, max_length=2000)
    category: str = Field(min_length=2, max_length=60)
    location: str = Field(min_length=2, max_length=120)
    image_path: Optional[str] = None
    report_type: Literal["lost", "found"] = "lost"
    reported_at: Optional[datetime] = None


class MatchResult(BaseModel):
    item_id: str
    score: float
    reason: str = ""


class MatchingEngine:
    def __init__(self):
        self.reports: List[ItemReport] = []

    def add_report(self, report: ItemReport):
        self.reports.append(report)

    def find_matches(
        self,
        target: ItemReport,
        threshold: float = 0.50,
    ) -> List[MatchResult]:
        results = []

        for report in self.reports:
            if target.item_id and report.item_id == target.item_id:
                continue
            if target.report_type == report.report_type:
                continue

            score = self._calculate_score(target, report)
            if score >= threshold:
                results.append(
                    MatchResult(
                        item_id=report.item_id or "",
                        score=round(score, 2),
                        reason="Similar description, category, location, or report date",
                    )
                )

        results.sort(key=lambda result: result.score, reverse=True)
        return results

    def _calculate_score(self, a: ItemReport, b: ItemReport) -> float:
        weighted_score = 0.0
        available_weight = 0.0

        description_weight = 0.60
        description_a = self._words(a.description)
        description_b = self._words(b.description)
        if description_a and description_b:
            overlap = len(description_a & description_b)
            description_similarity = (2 * overlap) / (len(description_a) + len(description_b))
            weighted_score += description_weight * description_similarity
            available_weight += description_weight

        category_weight = 0.20
        if a.category and b.category:
            weighted_score += category_weight * self._text_similarity(a.category, b.category)
            available_weight += category_weight

        location_weight = 0.12
        if a.location and b.location:
            weighted_score += location_weight * self._text_similarity(a.location, b.location)
            available_weight += location_weight

        time_weight = 0.08
        if a.reported_at and b.reported_at:
            days_apart = abs((a.reported_at - b.reported_at).total_seconds()) / 86400
            time_similarity = max(0.0, 1.0 - days_apart / 30)
            weighted_score += time_weight * time_similarity
            available_weight += time_weight

        if available_weight == 0:
            return 0.0
        return weighted_score / available_weight

    @staticmethod
    def _words(text: str) -> set[str]:
        return {word.strip(".,!?;:()[]{}\"'").casefold() for word in text.split()} - {""}

    @classmethod
    def _text_similarity(cls, first: str, second: str) -> float:
        first_normalized = " ".join(first.casefold().split())
        second_normalized = " ".join(second.casefold().split())
        if first_normalized == second_normalized:
            return 1.0

        first_words = cls._words(first_normalized)
        second_words = cls._words(second_normalized)
        if not first_words or not second_words:
            return 0.0
        return (2 * len(first_words & second_words)) / (len(first_words) + len(second_words))
