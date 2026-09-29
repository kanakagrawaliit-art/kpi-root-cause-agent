import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)  # fixed seed = same data every run (reproducible)
dates = pd.date_range("2024-04-01", "2024-05-07")

# Each device: (share of traffic, normal conversion rate)
devices = {"iOS": (0.30, 0.045), "Android": (0.40, 0.042), "Web": (0.30, 0.050)}
countries = {"US": 0.5, "UK": 0.2, "IN": 0.3}       # traffic share per country
channels = {"organic": 0.4, "paid": 0.4, "email": 0.2}
products = {"basic": 0.6, "premium": 0.4}

rows = []
# Loop over every date x device x country x channel x product combination
for d in dates:
    for dev, (dev_share, base_rate) in devices.items():
        for c, c_share in countries.items():
            for ch, ch_share in channels.items():
                for p, p_share in products.items():
                    # Sessions ~ Poisson around (total daily traffic x all the shares)
                    sessions = rng.poisson(6000 * dev_share * c_share * ch_share * p_share)
                    rate = base_rate
                    # PLANTED PROBLEM: Android conversion falls 30% from May 3
                    if dev == "Android" and d >= pd.Timestamp("2024-05-03"):
                        rate *= 0.70
                    # Conversions ~ Binomial(sessions, rate); revenue ~ ~$60 per conversion
                    conv = rng.binomial(sessions, rate)
                    revenue = round(float(conv * rng.normal(60, 5)), 2)
                    rows.append([d.date(), dev, c, ch, p, sessions, conv, revenue])

out = Path("data/raw")
out.mkdir(parents=True, exist_ok=True)

# Write the main KPI table
pd.DataFrame(rows, columns=["date", "device", "country", "channel", "product",
                            "sessions", "conversions", "revenue"]).to_csv(out / "kpi_daily.csv", index=False)

# Write the events table the get_event_context tool will read
pd.DataFrame([
    ["2024-04-10", "campaign", "Spring paid promo launched"],
    ["2024-05-03", "release", "Android app release 7.4 rolled out to 100%"],
], columns=["date", "event_type", "description"]).to_csv(out / "events.csv", index=False)
print("Sample data written.")