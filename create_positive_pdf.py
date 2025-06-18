import pandas as pd
from pathlib import Path

# Tạo dữ liệu mẫu về chứng khoán bằng tiếng Anh
data = {
    "Stock Symbol": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
    "Company Name": ["Apple Inc.", "Alphabet Inc.", "Microsoft Corp.", "Amazon.com Inc.", "Tesla Inc."],
    "Sector": ["Technology", "Technology", "Technology", "Consumer Discretionary", "Consumer Discretionary"],
    "Market Cap (Billion USD)": [2800, 1700, 2500, 1600, 900],
    "Stock Price (USD)": [185.0, 130.5, 320.3, 125.8, 210.2],
    "PE Ratio": [29.5, 24.8, 31.1, 42.6, 75.2]
}

# Tạo DataFrame
df = pd.DataFrame(data)

# Lưu vào file Excel
output_path = Path("./raw_docs/stock_sample_data.xlsx")
df.to_excel(output_path, index=False)

output_path.name
