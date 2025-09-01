#!/usr/bin/env python3

"""
Test the URL normalization logic for streamable-http transport
"""

from urllib.parse import urlparse, urlunparse
from typing import Any


def normalize_mcp_endpoint(
    raw_url: str, transport: str
) -> tuple[str, str, dict[str, Any]]:
    """
    Normalize MCP endpoint URL and transport for consistent client usage.
    This is the same function from tools_manager.py
    """
    extras = {}

    parsed = urlparse(raw_url)
    # Capture fragment (container name) if present
    container = parsed.fragment if parsed.fragment else None

    # Strip fragment (HTTP clients won't send it anyway)
    parsed = parsed._replace(fragment="")

    # Normalize transport string
    t = transport.lower().strip()
    if t in ("stdio", "sse"):
        t = "sse"
        # Force /sse path
        path = parsed.path.rstrip("/")
        if not path.endswith("/sse"):
            path = f"{path}/sse" if path else "/sse"
        parsed = parsed._replace(path=path)
    elif t in ("http", "streamable-http", "streamable"):
        t = "streamable-http"  # Use full name for Smolagents compatibility
        # Force /mcp/ path (note the trailing slash is important for FastMCP)
        path = parsed.path.rstrip("/")
        if not path.endswith("/mcp"):
            path = f"{path}/mcp" if path else "/mcp"
        # Add trailing slash for FastMCP compatibility
        path = f"{path}/"
        parsed = parsed._replace(path=path)
    else:
        raise ValueError(f"Unsupported transport: {transport}")

    url = urlunparse(parsed)

    # Store container hint for logging/debugging
    if container:
        extras["container_hint"] = container
        print(
            f"⚠️ ToolHive container fragment '{container}' detected but fragments are not sent over HTTP. "
            f"Container selection may be ignored unless handled by the MCP server."
        )

    return url, t, extras


def test_normalize_endpoint():
    """Test the normalize_mcp_endpoint function"""
    print("Testing URL normalization for MCP endpoints...")
    print("=" * 50)

    test_cases = [
        # (input_url, transport, expected_url, expected_transport)
        (
            "http://127.0.0.1:5002",
            "streamable-http",
            "http://127.0.0.1:5002/mcp/",
            "streamable-http",
        ),
        (
            "http://127.0.0.1:5002",
            "http",
            "http://127.0.0.1:5002/mcp/",
            "streamable-http",
        ),
        (
            "http://127.0.0.1:5002/mcp",
            "streamable-http",
            "http://127.0.0.1:5002/mcp/",
            "streamable-http",
        ),
        (
            "http://127.0.0.1:5002/",
            "streamable-http",
            "http://127.0.0.1:5002/mcp/",
            "streamable-http",
        ),
        ("http://127.0.0.1:5002", "sse", "http://127.0.0.1:5002/sse", "sse"),
        (
            "http://127.0.0.1:5002/sse#container",
            "sse",
            "http://127.0.0.1:5002/sse",
            "sse",
        ),
    ]

    passed = 0
    failed = 0

    for input_url, transport, expected_url, expected_transport in test_cases:
        try:
            result_url, result_transport, extras = normalize_mcp_endpoint(
                input_url, transport
            )

            if result_url == expected_url and result_transport == expected_transport:
                print(
                    f"✅ {input_url} ({transport}) → {result_url} ({result_transport})"
                )
                passed += 1
            else:
                print(
                    f"❌ {input_url} ({transport}) → {result_url} ({result_transport})"
                )
                print(f"   Expected: {expected_url} ({expected_transport})")
                failed += 1

        except Exception as e:
            print(f"❌ {input_url} ({transport}) → Error: {e}")
            failed += 1

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All URL normalization tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False


def main():
    """Run the URL normalization tests"""
    success = test_normalize_endpoint()

    print("\nThese normalized URLs should work with the updated Toolomics servers:")
    print("- http://127.0.0.1:5002/mcp/ (CSV server)")
    print("- http://127.0.0.1:5003/mcp/ (Search server)")
    print("- http://127.0.0.1:5004/mcp/ (PDF server)")
    print("- etc.")

    return success


if __name__ == "__main__":
    main()
