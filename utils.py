def apply_filter(df, filter_dict):
    for k, v in filter_dict.items():
        df = df.filter(f"{k} == '{v}'")
    return df

def dict_to_sql_filter(filter_dict):
    return " AND ".join([f"{k} = '{v}'" for k, v in filter_dict.items()])
