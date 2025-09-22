import pandas as pd

def process_stations_info(file_path, sheets, lat_col, lon_col, name_col, out_path, rename_map=None):

    xls = pd.ExcelFile(file_path)

    dfs = []

    for sheet in sheets:
        df = pd.read_excel(xls, sheet_name=sheet)
        df['sheet_name'] = sheet
        dfs.append(df[[lat_col, lon_col, name_col, 'sheet_name']])

    all_data = pd.concat(dfs, ignore_index=True)

    grouped = all_data.groupby([lat_col, lon_col, name_col])

    filtered = grouped.filter(lambda x: x['sheet_name'].nunique() > 1)


    # filtered = filtered.drop_duplicates(subset=[lat_col, lon_col, name_col])

    filtered = filtered.reset_index(drop=True)

    if rename_map:
        filtered = filtered.rename(columns=rename_map)

    # filtered.to_excel(out_path, index=False)

    return filtered



def select_data(xlsx_path, lat_col, lon_col, sheet_name=None):
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, engine='openpyxl')
    return df[lat_col],df[lon_col]