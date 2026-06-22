import os
import uuid
import pandas as pd
import matplotlib.pyplot as plt

from langchain_core.tools import tool

from utils.dataframe_store import load_dataframe

FORBIDDEN = [
    "import os",
    "import subprocess",
    "import socket",
    "open(",
    "eval(",
    "exec(",
    "__import__",
    "system(",
    "remove(",
    "unlink("
]

@tool
def inspect_data(dataset_id: str) -> str:
    """
    Inspect dataset structure.
    """

    df = load_dataframe(dataset_id)

    report = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": df.isnull().sum().to_dict()
    }

    return str(report)

@tool
def execute_python(
    dataset_id: str,
    code: str
) -> str:
    """
    Execute pandas code on dataframe.

    Result must be stored in variable result.
    """

    for forbidden in FORBIDDEN:

        if forbidden.lower() in code.lower():
            return f"Blocked: {forbidden}"

    df = load_dataframe(dataset_id)

    local_scope = {
        "df": df,
        "pd": pd
    }

    try:

        exec(code, {}, local_scope)

        if "result" not in local_scope:
            return "Variable result not found"

        return str(local_scope["result"])

    except Exception as e:

        return f"ERROR: {str(e)}"
    
@tool
def create_plot(
    dataset_id: str,
    code: str
) -> str:
    """
    Create matplotlib plot.

    Save image and return path.
    """

    df = load_dataframe(dataset_id)

    local_scope = {
        "df": df,
        "plt": plt
    }

    try:

        exec(code, {}, local_scope)

        filename = os.path.abspath(
            f"plots/{uuid.uuid4()}.png"
    )
        plt.savefig(
            filename,
            bbox_inches="tight"
        )

        plt.close()

        return filename

    except Exception as e:

        return f"ERROR: {str(e)}"