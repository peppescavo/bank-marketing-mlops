import pandas as pd 

def missing_summary(df):
    count = df.isna().sum()
    percentage = df.isna().mean() * 100

    return (
        pd.DataFrame({
            "missing_count": count,
            "missing_percentage": percentage
        })
        .sort_values("missing_percentage", ascending=False)
    )



def find_unknown_like_values(df):

    unknown_tokens = {
        "unknown",
        "unk",
        "n/a",
        "na",
        "none",
        "null",
        "missing",
        "not available",
        "not applicable",
        "unspecified",
        "?",
        "-",
        ""
    }

    results = []

    for column in df.columns:

        if df[column].dtype in ["object", "string"]:

            normalized = df[column].astype(str).str.strip().str.lower()

            mask = normalized.isin(unknown_tokens)

            if mask.any():

                results.append({
                    "column": column,
                    "count": mask.sum(),
                    "percentage": mask.mean() * 100
                })

    return pd.DataFrame(results)