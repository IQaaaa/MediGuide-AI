"""In-memory and SQLite cache management for LangChain."""

from pathlib import Path
from typing import Literal

from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

from .config import CACHE_DB_PATH

CacheType = Literal["None", "InMemoryCache", "SQLiteCache"]


def configure_cache(cache_type: CacheType) -> None:
    """
    Register the selected LangChain cache globally.

    LangChain automatically checks the registered cache before an LLM call.
    """
    if cache_type == "InMemoryCache":
        set_llm_cache(InMemoryCache())
    elif cache_type == "SQLiteCache":
        Path(CACHE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        set_llm_cache(SQLiteCache(database_path=CACHE_DB_PATH))
    else:
        set_llm_cache(None)


def cache_description(cache_type: CacheType) -> str:
    if cache_type == "InMemoryCache":
        return "RAM cache: fastest, but it is lost when the Python process stops."
    if cache_type == "SQLiteCache":
        return (
            "Disk cache: stored in mediguide_cache.db and can survive app restarts."
        )
    return "Caching is disabled."
