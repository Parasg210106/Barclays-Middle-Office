import pandas as pd
import os

def load_trades(file_path):
    ext = os.path.splitext(file_path)[1]
    if ext == '.csv':
        return pd.read_csv(file_path)
    elif ext in ['.xls', '.xlsx']:
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type")

def filter_trades_by_event(df, event_column='event_type'):
    import pandas as pd
    events = ['Early-Redemption', 'Barrier-Monitoring', 'Coupon Rate', 'Maturity']
    filtered = {event: pd.DataFrame(columns=df.columns) for event in events}
    for idx, row in df.iterrows():
        event = row.get(event_column, '')
        if pd.isna(event) or not str(event).strip():
            event = 'Maturity'
        else:
            event = str(event).strip()
        if event in filtered:
            filtered[event] = pd.concat([filtered[event], pd.DataFrame([row])], ignore_index=True)
    return filtered

def save_filtered_trades(filtered, output_dir='filtered_trades'):
    os.makedirs(output_dir, exist_ok=True)
    for event, trades in filtered.items():
        trades.to_csv(os.path.join(output_dir, f"{event.replace(' ', '_')}.csv"), index=False) 

