# CleanAir AI — Model Card

## Model Name

CleanAir AI AQI Forecasting Model

## Best Model

Random Forest

## Purpose

The model predicts the next available AQI timestamp for each monitoring station using recent AQI history, station context, weather features, geospatial proxy features, and source attribution signals.

## Training Data

- Source: CPCB/data.gov.in AQI API
- History rows: 5644
- Unique timestamps: 12
- Unique stations: 488
- Training rows: 4124
- Test rows: 1032

## Performance

- MAE: 14.5002
- RMSE: 39.879
- R2: 0.8718
- Category accuracy: 0.8905
- High AQI precision: 0.9634
- High AQI recall: 0.9922
- High AQI F1-score: 0.9776

## Strengths

- Uses real AQI snapshots collected from the live AQI API.
- Compares multiple models instead of relying on a single model.
- Performs strong high-AQI detection.
- Produces uncertainty bounds using residual spread.
- Connects forecasting with hotspot ranking and intervention recommendation.

## Limitations

- Current training history contains only 12 timestamps.
- Forecasting is suitable for prototype-level short-term AQI prediction.
- More historical data over multiple days or weeks would improve generalization.
- Satellite aerosol score is a proxy, not direct satellite imagery.

## Intended Use

- Short-term AQI forecasting
- Hotspot identification
- City/station prioritization
- Decision-support dashboard
- Prototype-level environmental intelligence system

## Not Intended For

- Legal enforcement without human verification
- Medical diagnosis
- Long-range climate prediction
- Final government policy decision without official validation

## Saved Model File

`C:\Users\Lenovo\Desktop\CleanAir_AI\models\best_aqi_forecast_model.pkl`
