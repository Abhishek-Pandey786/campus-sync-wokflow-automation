# Scripts - Utility and Automation Scripts

This directory contains helper scripts for development and data management.

## Scripts

### Database Management

- `seed_data.py` - Populate database with initial test data (Week 1)
- `reset_db.py` - Reset database to clean state
- `backup_db.py` - Create database backup

### Data Generation

- `generate_synthetic_data.py` - Create synthetic workflow dataset (Week 4)
- `export_logs.py` - Export workflow logs for ML training

### ML Pipeline

- `train_models.py` - Train 5 ML models (LR, RF, GB, SVM, MLP) and save best (Week 5+)
- `evaluate_model.py` - Generate model evaluation reports

> See also: `notebooks/model_comparison.ipynb` — full 5-model EDA, training, and ROC comparison

### Testing

- `load_test.py` - API load testing
- `validate_data.py` - Data quality validation

## Usage

Run scripts from the backend directory:

```bash
cd backend
python ../scripts/seed_data.py
```

## Current Status

✅ seed_data.py — seeds 1,201 synthetic requests  
✅ generate_synthetic_data.py — creates ML training dataset  
✅ train_models.py — trains 5 models, saves best (LR at 98.68%)  
✅ evaluate_model.py — generates metrics report
