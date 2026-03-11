# Data Directory

This directory contains datasets for training and evaluation.

## Structure

```
data/
├── raw/                  # Original synthetic/real data
│   ├── synthetic_requests.csv
│   └── .gitkeep
│
├── processed/            # Cleaned and feature-engineered data
│   ├── train.csv
│   ├── test.csv
│   └── .gitkeep
│
└── exports/              # Exported reports and visualizations
    └── .gitkeep
```

## Dataset Generation (Week 4)

**✅ COMPLETED**

Synthetic dataset has been generated with:

- ✅ 1,200 service request records
- ✅ Features: request_type, priority, stage durations, handler_workload, temporal features (18 total)
- ✅ Target: is_delayed (binary: 0=on-time, 1=delayed)
- ✅ Realistic distribution (~60% on-time, ~40% delayed)
- ✅ SLA-based delay classification
- ✅ Business hour and weekday patterns

**Generation Script**: `../scripts/generate_synthetic_data.py`  
**Analysis Script**: `../scripts/analyze_data.py`  
**Output**: `raw/synthetic_requests.csv` (150 KB)

**Next Step**: Week 5 - ML Model Training

## Data Privacy

All data is synthetic or anonymized. No real student information is stored.
