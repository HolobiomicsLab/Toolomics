import httpx
from os import getenv
from bs4 import BeautifulSoup
from pydantic import BaseModel


class SearchResult(BaseModel):
    url: str
    title: str
    content: str


class InfoboxUrl(BaseModel):
    title: str
    url: str


class Infobox(BaseModel):
    infobox: str
    id: str
    content: str
    urls: list[InfoboxUrl]


class Response(BaseModel):
    query: str
    number_of_results: int
    results: list[SearchResult]
    infoboxes: list[Infobox]


async def search_searx(query, limit: int = 3):
    """
    Recherche asynchrone sur une instance SearxNG et extrait les URLs, titres et descriptions.

    Args:
        query (str): La requête de recherche

    Returns:
        str: Résultats formatés ou message d'erreur
    """
    base_url = str(getenv("SEARXNG_URL", "http://localhost:8080"))
    if not query or query.strip() == "":
        return "Error: Empty search query provided."

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": user_agent,
    }
    query = query.strip()
    # encoded_query = quote(query)
    params: dict[str, str] = {"q": query, "format": "json"}
    # data = f"q={encoded_query}&categories=general&language=auto&time_range=&safesearch=0&theme=simple".encode("utf-8")

    try:
        async with httpx.AsyncClient(base_url=base_url) as client:
            response = await client.post("/search", headers=headers, params=params)
            response.raise_for_status()

            data = Response.model_validate_json(response.text)
            
            text  = ""

            for index, infobox in enumerate(data.infoboxes):
                text += f"Infobox: {infobox.infobox}\n"
                text += f"ID: {infobox.id}\n"
                text += f"Content: {infobox.content}\n"
                text += "\n"

            if len(data.results) == 0:
                text += "No results found\n"

            for index, result in enumerate(data.results):
                text += f"Title: {result.title}\n"
                text += f"URL: {result.url}\n"
                text += f"Content: {result.content}\n"
                text += "\n"

                if index == limit - 1:
                    break

            return str(text)
    except httpx.RequestError as e:
        return f"Error: SearxNG search failed. {str(e)}\n"
