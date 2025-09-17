import pandas as pd
from sklearn.preprocessing import StandardScaler

def scaler(df_cleaned: pd.DataFrame) -> pd.DataFrame:
    scale_cols = ['search_volume', 'competing_products']
    ss = StandardScaler()

    scaled_array = ss.fit_transform(df_cleaned[scale_cols])
    scaled_df = pd.DataFrame(scaled_array, columns=scale_cols)

    result_df = pd.concat([df_cleaned['keyword'], scaled_df], axis=1)
    result_df['value_score'] = ((result_df['search_volume'] + 1) / (result_df['competing_products'] + 1))
    return result_df
