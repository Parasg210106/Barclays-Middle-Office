import os
from main import load_trades, filter_trades_by_event, save_filtered_trades

def run_lifecycle_filter(file_path, event_column='event_type', output_dir='db/output'):
    df = load_trades(file_path)
    filtered = filter_trades_by_event(df, event_column=event_column)
    save_filtered_trades(filtered, output_dir=output_dir)


if __name__ == "__main__":
    file_path = 'db/raw/trades.csv'  # Update to new location
    run_lifecycle_filter(file_path) 