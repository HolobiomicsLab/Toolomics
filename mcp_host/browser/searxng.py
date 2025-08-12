import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


def search_searx(query):
    """
    Searches a SearxNG instance and extracts URLs, titles, and descriptions.

    Args:
        query (str): The search query
        base_url (str, optional): Base URL for SearxNG instance. Defaults to env var SEARXNG_BASE_URL.

    Returns:
        str: Formatted search results or error message
    """
    # Try container service name first, then fallback options
    base_url_candidates = [
        "http://searxng:8080",  # Docker service name (preferred)
        "http://localhost:8080",  # Local development
        "http://0.0.0.0:8080",  # Original fallback
        "http://host.docker.internal:8080",  # Docker Desktop
    ]

    base_url = None
    for url in base_url_candidates:
        try:
            # Quick connectivity test
            response = requests.get(f"{url}/", timeout=2)
            if response.status_code == 200:
                base_url = url
                break
        except:
            continue

    if not base_url:
        base_url = base_url_candidates[0]  # Use first as fallback
    if not base_url:
        return "Error: SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable."

    if not query or query.strip() == "":
        return "Error: Empty search query provided."

    search_url = f"{base_url}/search"
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
    encoded_query = quote(query)
    data = f"q={encoded_query}&categories=general&language=auto&time_range=&safesearch=0&theme=simple".encode(
        "utf-8"
    )

    try:
        response = requests.post(search_url, headers=headers, data=data, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for article in soup.find_all("article", class_="result"):
            url_header = article.find("a", class_="url_header")
            if url_header:
                url = url_header["href"]
                title = (
                    article.find("h3").text.strip()
                    if article.find("h3")
                    else "No Title"
                )
                description = (
                    article.find("p", class_="content").text.strip()
                    if article.find("p", class_="content")
                    else "No Description"
                )
                results.append(f"Title:{title}\nSnippet:{description}\nLink:{url}")

        if len(results) == 0:
            return "No search results, web search failed. Consider using a different query or waiting a few minutes before trying again. If all fail, request user assistance."
        return "\n\n".join(results)

    except requests.exceptions.RequestException as e:
        return f"Error: SearxNG search failed. {str(e)}\n"


def check_link_validity(link):
    """
    Check if a link is valid and accessible.
    Args:
        link (str): URL to check
    Returns:
        str: Status message about the link
    """
    paywall_keywords = [
        "Member-only",
        "access denied",
        "restricted content",
        "404",
        "this page is not working",
    ]

    if not link.startswith("http"):
        return "Status: Invalid URL"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(link, headers=headers, timeout=5)
        status = response.status_code
        if status == 200:
            content = response.text.lower()
            if any(keyword.lower() in content for keyword in paywall_keywords):
                return "Status: Possible Paywall"
            return "Status: OK"
        elif status == 404:
            return "Status: 404 Not Found"
        elif status == 403:
            return "Status: 403 Forbidden"
        else:
            return f"Status: {status} {response.reason}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    result = search_searx("are dogs better than cats?")
    print(result)
