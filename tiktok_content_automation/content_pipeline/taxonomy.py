from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    name: str
    topics: tuple[str, ...]
    search_terms: tuple[str, ...]
    keywords: tuple[str, ...]


CATEGORIES: tuple[Category, ...] = (
    Category(
        name="Marriage Lessons From Famous Men",
        topics=("Marriage", "Commitment", "Celebrity relationship perspectives"),
        search_terms=(
            "famous men marriage advice interview",
            "celebrity husband marriage advice interview",
            "successful men talk about marriage wife interview",
            "athlete explains marriage wife interview",
            "rapper talks about wife marriage interview",
        ),
        keywords=(
            "marriage",
            "married",
            "wife",
            "husband",
            "commitment",
            "backbone",
            "family",
            "loyalty",
            "vows",
        ),
    ),
    Category(
        name="Why Men Don’t Commit",
        topics=("Commitment", "Why people stay single", "Women’s standards vs men’s standards"),
        search_terms=(
            "why men don't commit relationship interview",
            "men explain why they stay single podcast",
            "man explains why he won't get married interview",
            "dating standards why men avoid commitment podcast",
            "why successful men stay single relationship advice",
        ),
        keywords=(
            "commit",
            "commitment",
            "single",
            "settle down",
            "girlfriend",
            "marry",
            "standards",
            "options",
            "dating",
        ),
    ),
    Category(
        name="What Women Actually Want",
        topics=("Respect in relationships", "Women’s standards vs men’s standards"),
        search_terms=(
            "what women want in a man relationship interview",
            "women standards in dating podcast clip",
            "relationship advice what women need from men interview",
            "man explains what keeps a woman happy interview",
            "respect women relationship advice podcast",
        ),
        keywords=(
            "women want",
            "woman wants",
            "respect",
            "provide",
            "protect",
            "safe",
            "listen",
            "standards",
            "happy",
            "communication",
        ),
    ),
    Category(
        name="Modern Dating Truths",
        topics=("Why people stay single", "Respect in relationships", "Women’s standards vs men’s standards"),
        search_terms=(
            "modern dating truth relationship podcast",
            "why dating is hard today podcast clip",
            "single people relationship advice interview",
            "men women dating standards debate interview",
            "relationship truth about respect loyalty podcast",
        ),
        keywords=(
            "modern dating",
            "dating today",
            "single",
            "respect",
            "loyalty",
            "standards",
            "relationships",
            "red flags",
            "accountability",
        ),
    ),
    Category(
        name="Celebrity Relationship Advice",
        topics=("Celebrity relationship perspectives", "Marriage", "Commitment"),
        search_terms=(
            "celebrity relationship advice interview",
            "celebrity talks about love marriage interview",
            "actor relationship advice interview love marriage",
            "rapper relationship advice love interview",
            "athlete relationship advice marriage interview",
        ),
        keywords=(
            "celebrity",
            "interview",
            "love",
            "relationship",
            "marriage",
            "wife",
            "girlfriend",
            "dating",
            "commitment",
        ),
    ),
)


CATEGORY_BY_NAME = {category.name: category for category in CATEGORIES}
