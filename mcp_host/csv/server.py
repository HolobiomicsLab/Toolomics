#!/usr/bin/env python3

"""
CSV Management MCP Server

Provides tools for creating, reading, and manipulating CSV files.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import sys
import os
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import get_workspace_path

description = """CSV Management MCP Server provides tools for creating, reading, and manipulating CSV files.
It allows users to create new CSV datasets, load existing CSV files, and perform various operations on them such as adding, updating, deleting rows, and querying data.
"""

mcp = FastMCP(
    name="CSV Management MCP",
    instructions=description,
)


@mcp.tool
def get_mcp_name() -> str:
    """Get the name of this MCP server"""
    return "CSV Management"


# Default working directory for CSV files - use shared workspace
CSV_DIR = get_workspace_path()
CSV_DIR.mkdir(exist_ok=True)


def _get_csv_path(name: str) -> Path:
    """Get the full path for a CSV file, ensuring it's in our CSV directory."""
    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in "._-")
    if not safe_name.endswith(".csv"):
        safe_name += ".csv"
    return CSV_DIR / safe_name


def _load_dataframe(name: str) -> pd.DataFrame:
    """Load a DataFrame from CSV file."""
    csv_path = _get_csv_path(name)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset '{name}' not found")
    return pd.read_csv(csv_path)


def _save_dataframe(name: str, df: pd.DataFrame) -> None:
    """Save a DataFrame to CSV file."""
    csv_path = _get_csv_path(name)
    df.to_csv(csv_path, index=False)


@mcp.tool
def create_csv(
    name: str,
    columns: Optional[List[str]] = None,
    rows: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create a new CSV dataset.

    Args:
        name: Name of the dataset
        columns: List of column names (optional)
        rows: List of row dictionaries (optional)

    Returns:
        Dictionary with dataset info
    """
    try:
        if columns and rows:
            df = pd.DataFrame(rows, columns=columns)
        elif columns:
            df = pd.DataFrame(columns=columns)
        elif rows:
            df = pd.DataFrame(rows)
        else:
            df = pd.DataFrame()

        _save_dataframe(name, df)

        return {
            "name": name,
            "shape": list(df.shape),
            "columns": df.columns.tolist(),
            "message": f"Dataset '{name}' created successfully",
            "status": "success",
        }
    except Exception as e:
        return {"status": str(e)}


@mcp.tool
def load_csv_from_path(source_path: str, name: str) -> Dict[str, Any]:
    """
    Load a CSV file from an external path into our managed datasets.

    Args:
        source_path: Path to the source CSV file
        name: Name to give the dataset

    Returns:
        Dictionary with dataset info and preview
    """
    try:
        source = Path(source_path)
        if not source.exists():
            return {"error": f"Source file '{source_path}' not found"}

        df = pd.read_csv(source)
        _save_dataframe(name, df)

        return {
            "name": name,
            "shape": list(df.shape),
            "columns": df.columns.tolist(),
            "preview": df.head(5).to_dict("records"),
            "message": f"Dataset '{name}' loaded from '{source_path}'",
            "status": "success",
        }
    except Exception as e:
        return {"status": str(e)}


@mcp.tool
def get_csv_data(
    name: str, limit: Optional[int] = None, offset: int = 0
) -> Dict[str, Any]:
    """
    Get data from a CSV dataset.

    Args:
        name: Name of the dataset
        limit: Maximum number of rows to return
        offset: Number of rows to skip from the beginning

    Returns:
        Dictionary with data and metadata
    """
    try:
        df = _load_dataframe(name)

        if limit:
            data = df.iloc[offset : offset + limit].to_dict("records")
        else:
            data = df.iloc[offset:].to_dict("records")

        return {
            "data": data,
            "total_rows": len(df),
            "returned_rows": len(data),
            "offset": offset,
            "status": "success",
        }
    except Exception as e:
        return {"status": str(e)}


@mcp.tool
def add_csv_row(name: str, row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a row to a CSV dataset.

    Args:
        name: Name of the dataset
        row: Dictionary with row data

    Returns:
        Dictionary with updated dataset info
    """
    try:
        df = _load_dataframe(name)
        new_row = pd.DataFrame([row])
        df = pd.concat([df, new_row], ignore_index=True)
        _save_dataframe(name, df)

        return {
            "name": name,
            "shape": list(df.shape),
            "message": f"Row added to dataset '{name}'",
            "status": "success",
        }
    except Exception as e:
        return {"status": str(e)}


@mcp.tool
def update_csv_row(name: str, index: int, row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a row in a CSV dataset.

    Args:
        name: Name of the dataset
        index: Row index to update
        row: Dictionary with updated row data

    Returns:
        Dictionary with updated row info
    """
    try:
        df = _load_dataframe(name)

        if index >= len(df) or index < 0:
            return {"error": f"Row index {index} out of range"}

        for column, value in row.items():
            if column in df.columns:
                df.loc[index, column] = value

        _save_dataframe(name, df)

        return {
            "name": name,
            "updated_row": df.iloc[index].to_dict(),
            "message": f"Row {index} updated in dataset '{name}'",
            "status": "success",
        }
    except Exception as e:
        return {"status": str(e)}


@mcp.tool
def delete_csv_row(name: str, index: int) -> Dict[str, Any]:
    """
    Delete a row from a CSV dataset.

    Args:
        name: Name of the dataset
        index: Row index to delete

    Returns:
        Dictionary with updated dataset info
    """
    try:
        df = _load_dataframe(name)

        if index >= len(df) or index < 0:
            return {"error": f"Row index {index} out of range"}

        df = df.drop(index).reset_index(drop=True)
        _save_dataframe(name, df)

        return {
            "name": name,
            "shape": list(df.shape),
            "message": f"Row {index} deleted from dataset '{name}'",
            "status": "success",
        }
    except Exception as e:
        return {"status": str(e)}


@mcp.tool
def list_csv_datasets() -> Dict[str, Any]:
    """
    List all available CSV datasets.

    Returns:
        Dictionary with list of datasets
    """
    try:
        datasets = []
        for csv_file in CSV_DIR.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                datasets.append(
                    {
                        "name": csv_file.stem,
                        "shape": list(df.shape),
                        "columns": df.columns.tolist(),
                        "file_size": csv_file.stat().st_size,
                    }
                )
            except Exception as e:
                datasets.append(
                    {"name": csv_file.stem, "error": f"Failed to read: {str(e)}"}
                )

        return {"datasets": datasets, "total_count": len(datasets), "status": "success"}
    except Exception as e:
        return {"status": str(e)}


@mcp.tool
def delete_csv_dataset(name: str) -> Dict[str, Any]:
    """
    Delete a CSV dataset.

    Args:
        name: Name of the dataset to delete

    Returns:
        Dictionary with deletion status
    """
    try:
        csv_path = _get_csv_path(name)
        if csv_path.exists():
            csv_path.unlink()
            return {
                "message": f"Dataset '{name}' deleted successfully",
                "status": "success",
            }
        else:
            return {"status": f"Dataset '{name}' not found"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def query_csv(name: str, query: str) -> Dict[str, Any]:
    """
    Query a CSV dataset using pandas query syntax.

    Args:
        name: Name of the dataset
        query: Pandas query string (e.g., "age > 25 and city == 'New York'")

    Returns:
        Dictionary with query results
    """
    try:
        df = _load_dataframe(name)
        result = df.query(query)

        return {
            "name": name,
            "query": query,
            "results": result.to_dict("records"),
            "result_count": len(result),
            "total_rows": len(df),
            "status": "success",
        }
    except Exception as e:
        return {"status": str(e)}


@mcp.tool
def get_csv_stats(name: str) -> Dict[str, Any]:
    """
    Get statistical summary of a CSV dataset.

    Args:
        name: Name of the dataset

    Returns:
        Dictionary with statistical information
    """
    try:
        df = _load_dataframe(name)

        # Basic stats
        stats = {
            "name": name,
            "shape": list(df.shape),
            "columns": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
            "categorical_columns": df.select_dtypes(
                include=["object"]
            ).columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": df.duplicated().sum(),
        }

        # Add numeric statistics if there are numeric columns
        if stats["numeric_columns"]:
            stats["numeric_summary"] = df.describe().to_dict()

        return stats
    except Exception as e:
        return {"status": str(e)}


print("Starting CSV MCP server with streamable-http transport...")
if __name__ == "__main__":
    # Get port from environment variable (set by ToolHive) or command line argument as fallback
    port = None
    if "MCP_PORT" in os.environ:
        port = int(os.environ["MCP_PORT"])
        print(f"Using port from MCP_PORT environment variable: {port}")
    elif "FASTMCP_PORT" in os.environ:
        port = int(os.environ["FASTMCP_PORT"])
        print(f"Using port from FASTMCP_PORT environment variable: {port}")
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
        print(f"Using port from command line argument: {port}")
    else:
        print("Usage: python server.py <port>")
        print("Or set MCP_PORT/FASTMCP_PORT environment variable")
        sys.exit(1)

    print(f"Starting server on port {port}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
