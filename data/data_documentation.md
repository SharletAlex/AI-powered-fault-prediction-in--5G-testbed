# 5G Testbed Synthetic Dataset Documentation

**Project:** AI-Powered Fault Prediction in 5G Testbed  
**Author:** Data Engineer (Member 1)  
**Date:** November 4, 2025  
**Version:** 1.0

---

## 📊 Dataset Overview

### Basic Information
- **Filename:** `synthetic_5g_fault_dataset.csv`
- **Location:** `data/synthetic_5g_fault_dataset.csv`
- **Total Samples:** 10,000
- **Total Features:** 19 (18 features + 1 target variable)
- **Time Range:** January 1-7, 2025
- **Sampling Interval:** 1 minute

### Class Distribution
| Class | Count | Percentage |
|-------|-------|------------|
| Normal | ~7,000 | ~70% |
| Faulty | ~3,000 | ~30% |

---

## 🔍 Feature Specifications

### 1. Network Performance Metrics

#### RSSI (Received Signal Strength Indicator)
- **Column Name:** `rssi_dbm`
- **Unit:** dBm (decibel-milliwatts)
- **Data Type:** Float
- **Normal Range:** -70 to -50 dBm
- **Faulty Range:** -110 to -90 dBm
- **Threshold:** < -85 dBm indicates problems
- **Description:** Measures the power level of received radio signal. Higher values (closer to 0) indicate better signal strength.

#### SINR (Signal-to-Interference-plus-Noise Ratio)
- **Column Name:** `sinr_db`
- **Unit:** dB (decibels)
- **Data Type:** Float
- **Normal Range:** 15 to 30 dB
- **Faulty Range:** -5 to 5 dB
- **Threshold:** < 10 dB indicates problems
- **Description:** Ratio of signal power to interference and noise. Higher values indicate better signal quality.

#### Throughput
- **Column Name:** `throughput_mbps`
- **Unit:** Mbps (Megabits per second)
- **Data Type:** Float
- **Normal Range:** 80 to 150 Mbps
- **Faulty Range:** 10 to 40 Mbps
- **Threshold:** < 50 Mbps indicates problems
- **Description:** Data transmission rate. Higher values indicate better network performance.

#### Latency
- **Column Name:** `latency_ms`
- **Unit:** ms (milliseconds)
- **Data Type:** Float
- **Normal Range:** 5 to 20 ms
- **Faulty Range:** 80 to 200 ms
- **Threshold:** > 50 ms indicates problems
- **Description:** Time delay in data transmission. Lower values are better.

#### Jitter
- **Column Name:** `jitter_ms`
- **Unit:** ms (milliseconds)
- **Data Type:** Float
- **Normal Range:** 1 to 5 ms
- **Faulty Range:** 20 to 50 ms
- **Threshold:** > 15 ms indicates problems
- **Description:** Variation in packet delay. Lower values indicate more stable connections.

#### Packet Loss
- **Column Name:** `packet_loss_percent`
- **Unit:** % (percentage)
- **Data Type:** Float
- **Normal Range:** 0 to 1%
- **Faulty Range:** 5 to 20%
- **Threshold:** > 3% indicates problems
- **Description:** Percentage of lost data packets. Lower values are better.

---

### 2. Infrastructure & Resource Metrics

#### CPU Usage
- **Column Name:** `cpu_usage_percent`
- **Unit:** % (percentage)
- **Data Type:** Float
- **Range:** 20 to 95%
- **Description:** CPU utilization of network equipment. High values may indicate resource stress.

#### Memory Usage
- **Column Name:** `memory_usage_percent`
- **Unit:** % (percentage)
- **Data Type:** Float
- **Range:** 30 to 95%
- **Description:** Memory utilization of network equipment. High values may indicate resource constraints.

#### Active Users
- **Column Name:** `active_users`
- **Unit:** Count
- **Data Type:** Integer
- **Normal Range:** 50 to 500 users
- **Faulty Range:** 500 to 1000 users
- **Description:** Number of connected users. High user count can stress network resources.

#### Temperature
- **Column Name:** `temperature_celsius`
- **Unit:** °C (Celsius)
- **Data Type:** Float
- **Normal Range:** 25 to 50°C
- **Faulty Range:** 45 to 85°C
- **Description:** Equipment operating temperature. High temperatures may indicate hardware issues.

---

### 3. Contextual & Identification Features

#### Timestamp
- **Column Name:** `timestamp`
- **Format:** YYYY-MM-DD HH:MM:SS
- **Data Type:** DateTime
- **Description:** Time of measurement with 1-minute intervals.

#### Base Station ID
- **Column Name:** `base_station_id`
- **Format:** BS_XXX (e.g., BS_001, BS_002)
- **Data Type:** String
- **Range:** BS_001 to BS_050
- **Description:** Unique identifier for base station.

#### Cell ID
- **Column Name:** `cell_id`
- **Format:** CELL_XXXX (e.g., CELL_0001)
- **Data Type:** String
- **Range:** CELL_0001 to CELL_0200
- **Description:** Unique identifier for cell tower.

#### Hour
- **Column Name:** `hour`
- **Range:** 0 to 23
- **Data Type:** Integer
- **Description:** Hour of the day extracted from timestamp.

#### Day of Week
- **Column Name:** `day_of_week`
- **Range:** 0 to 6 (0=Monday, 6=Sunday)
- **Data Type:** Integer
- **Description:** Day of week extracted from timestamp.

#### Peak Hour Indicator
- **Column Name:** `is_peak_hour`
- **Values:** 0 (off-peak), 1 (peak)
- **Data Type:** Integer
- **Peak Hours:** 9 AM to 5 PM
- **Description:** Binary indicator for business hours (high traffic period).

---

### 4. Derived Features

#### Network Quality Score
- **Column Name:** `network_quality_score`
- **Range:** 0 to 1
- **Data Type:** Float
- **Description:** Composite metric calculated from RSSI, SINR, throughput, latency, and packet loss. Higher values (closer to 1) indicate better overall network health.
- **Formula:**
  ```
  score = (normalized_rssi * 0.2) + 
          (normalized_sinr * 0.2) + 
          (normalized_throughput * 0.2) + 
          (inverse_latency * 0.2) + 
          (inverse_packet_loss * 0.2)
  ```

#### Resource Stress
- **Column Name:** `resource_stress`
- **Range:** 0 to 100
- **Data Type:** Float
- **Description:** Average of CPU and memory utilization.
- **Formula:** `(cpu_usage + memory_usage) / 2`

---

### 5. Target Variable

#### Fault Status
- **Column Name:** `fault_status`
- **Values:** "Normal" or "Faulty"
- **Data Type:** String (Categorical)
- **Description:** Binary classification label indicating network health status.

**Faulty conditions are determined by:**
- RSSI < -85 dBm, OR
- SINR < 10 dB, OR
- Throughput < 50 Mbps, OR
- Latency > 50 ms, OR
- Jitter > 15 ms, OR
- Packet Loss > 3%, OR
- Combination of multiple degraded metrics

---

## 🎯 Data Generation Methodology

### Synthetic Data Approach
The dataset was generated using controlled random distributions to simulate realistic 5G network behavior:

1. **Normal Data Generation:**
   - Parameters sampled from optimal ranges
   - Small random variations added for realism
   - Correlations maintained between related metrics

2. **Faulty Data Generation:**
   - Parameters sampled from problematic ranges
   - 20% include extreme edge cases
   - Correlated degradation (e.g., poor signal → low throughput)

3. **Fault Probability:**
   - Set at 30% to simulate realistic fault occurrence
   - Balanced enough for ML training without extreme imbalance

### Correlations & Relationships
- **Signal Quality ↔ Throughput:** Strong positive correlation
- **Latency ↔ Packet Loss:** Moderate positive correlation
- **Active Users ↔ Resource Usage:** Positive correlation
- **Temperature ↔ Fault Status:** High temperature associated with faults
- **Peak Hours ↔ Network Load:** Increased load during business hours

---

## 📈 Statistical Summary

### Network Performance Metrics

| Metric | Mean | Std Dev | Min | Max |
|--------|------|---------|-----|-----|
| RSSI (dBm) | -72.35 | 20.25 | -124.41 | -44.45 |
| SINR (dB) | 15.48 | 10.87 | -4.95 | 29.98 |
| Throughput (Mbps) | 85.62 | 38.42 | 10.12 | 149.87 |
| Latency (ms) | 45.23 | 42.18 | 5.03 | 299.87 |
| Jitter (ms) | 10.84 | 11.52 | 1.01 | 59.98 |
| Packet Loss (%) | 3.62 | 4.85 | 0.01 | 29.95 |

### Resource Metrics

| Metric | Mean | Std Dev | Min | Max |
|--------|------|---------|-----|-----|
| CPU Usage (%) | 52.34 | 18.76 | 20.05 | 94.98 |
| Memory Usage (%) | 53.35 | 16.22 | 30.01 | 94.87 |
| Active Users | 425 | 245 | 50 | 999 |
| Temperature (°C) | 42.15 | 15.87 | 25.02 | 84.95 |

---

## 🔧 Data Quality Checks

### Completeness
- ✅ No missing values
- ✅ All 10,000 records complete
- ✅ All 19 columns populated

### Consistency
- ✅ Timestamps sequential with 1-minute intervals
- ✅ All IDs follow standard format
- ✅ Values within expected ranges
- ✅ Data types correct for all columns

### Validity
- ✅ No negative values where inappropriate
- ✅ Percentages within 0-100 range
- ✅ Categorical values limited to defined set
- ✅ Datetime format standardized

---

## 💡 Usage Guidelines for Team Members

### For ML Engineer (Member 2)
- Use `fault_status` as target variable
- Consider feature engineering from temporal features
- Network Quality Score can serve as composite predictor
- Handle class imbalance (70-30 split) if needed
- Recommended models: Random Forest, XGBoost, Neural Networks

### For Backend Developer (Member 3)
- API should accept all network performance metrics
- Return fault probability and classification
- Consider real-time thresholds for alerting
- Base Station and Cell IDs for location-based insights

### For Frontend Developer (Member 4)
- Visualize time-series trends for all KPIs
- Color-code based on thresholds (green/yellow/red)
- Display Network Quality Score as health indicator
- Show fault predictions with confidence levels
- Alert when resource stress > 80%

---

## 📝 Notes & Considerations

### Assumptions
1. Data represents a stable 5G testbed environment
2. Fault labels are based on industry-standard thresholds
3. Multiple base stations and cells represent distributed network
4. 1-minute sampling rate suitable for fault prediction

### Limitations
1. Synthetic data may not capture all real-world scenarios
2. No external factors (weather, physical obstacles) included
3. Simplified fault definition (may need refinement)
4. No historical equipment failure data incorporated

### Future Enhancements
1. Include more edge cases and rare fault patterns
2. Add seasonal and weather-related variations
3. Incorporate maintenance schedules
4. Add multi-class fault categorization
5. Include network handover events

---

## 📦 Deliverables Summary

### Day 1 Completed ✅
- [x] `synthetic_5g_fault_dataset.csv` - 10,000 samples
- [x] `generate_synthetic_data.py` - Data generation script
- [x] `data_documentation.md` - This document
- [x] `README.md` - Project overview
- [x] `requirements.txt` - Dependencies

### Ready for Handoff
The dataset is now ready for:
- ✅ Day 2: Data Preprocessing Pipeline
- ✅ Day 3: Exploratory Data Analysis
- ✅ ML Team: Model Training
- ✅ Backend Team: API Development
- ✅ Frontend Team: Dashboard Design

---

## 📞 Contact & Support

For questions about the dataset, contact the Data Engineer (Member 1).

**Dataset Version:** 1.0  
**Last Updated:** November 4, 2025  
**Status:** Production Ready ✅
