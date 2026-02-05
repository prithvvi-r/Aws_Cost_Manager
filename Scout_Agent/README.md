# AWS Cost Spike Detection Agent

## Overview
This agent monitors AWS costs across different services and regions to detect cost spikes. It compares current period costs against previous period costs and flags anomalies based on percentage change and absolute threshold values.

---

## Project Structure

```
agent1/
├── agent.py          # Main orchestration logic
├── ce_client.py      # AWS Cost Explorer API client
├── config.py         # Configuration parameters
├── detector.py       # Spike detection algorithm
├── parser.py         # Response parser
└── test_ce.py        # Testing script for Cost Explorer
```

---

## How It Works

### Workflow
1. **Fetch Cost Data**: Retrieves AWS cost data for current and previous time windows
2. **Parse Response**: Converts raw AWS API responses into structured cost dictionaries
3. **Detect Spikes**: Compares periods and identifies anomalies based on thresholds
4. **Return Results**: Outputs list of suspicious cost increases

---

## File-by-File Breakdown

### 1. `agent.py` - Main Orchestrator
**Purpose**: Entry point that coordinates the entire cost spike detection process

**Function: `run()`**
- **Input**: None (uses config values)
- **Output**: List of detected cost spikes with details
- **Working**:
  1. Initializes Cost Explorer client
  2. Fetches cost data for current window (Jan 15-29, 2025)
  3. Fetches cost data for previous window (Jan 1-15, 2025)
  4. Parses both raw responses
  5. Runs spike detection algorithm
  6. Returns anomaly list

---

### 2. `ce_client.py` - AWS Cost Explorer Client
**Purpose**: Handles AWS Cost Explorer API communication

**Class: `CostExplorerClient`**

**Method: `__init__()`**
- **Input**: None
- **Output**: Initialized boto3 Cost Explorer client
- **Working**: Creates AWS CE client in us-east-1 region (CE is global service)

**Method: `get_cost_by_service_region(start_date, end_date)`**
- **Input**: 
  - `start_date` (string): Start date in YYYY-MM-DD format
  - `end_date` (string): End date in YYYY-MM-DD format
- **Output**: Raw AWS Cost Explorer API response
- **Working**:
  - Calls `get_cost_and_usage` API
  - Sets monthly granularity
  - Requests UnblendedCost metric
  - Groups data by SERVICE and REGION dimensions

---

### 3. `config.py` - Configuration Settings
**Purpose**: Centralized configuration for detection parameters and time windows

**Parameters**:
- `PCT_THRESHOLD = 30`: Percentage increase threshold (30% change triggers alert)
- `ABS_THRESHOLD = 1000`: Absolute cost threshold ($1000+ triggers alert)
- `CURRENT_WINDOW = ("2025-01-15", "2025-01-29")`: Current monitoring period (14 days)
- `PREVIOUS_WINDOW = ("2025-01-01", "2025-01-15")`: Comparison baseline period (14 days)

---

### 4. `detector.py` - Spike Detection Logic
**Purpose**: Analyzes cost data to identify anomalies

**Function: `detect_spikes(current, previous, pct_threshold=30, abs_threshold=1000)`**
- **Input**:
  - `current` (dict): Current period costs {(service, region): cost}
  - `previous` (dict): Previous period costs {(service, region): cost}
  - `pct_threshold` (int): Percentage change threshold (default: 30%)
  - `abs_threshold` (int): Absolute cost threshold (default: $1000)
  
- **Output**: List of dictionaries containing spike details:
  ```python
  [
    {
      "service": "EC2",
      "region": "us-east-1",
      "current_cost": 1500.00,
      "previous_cost": 1000.00,
      "change_pct": 50.00,
      "time_window": "last_14_days"
    }
  ]
  ```

- **Working**:
  1. Iterates through current period costs
  2. Retrieves corresponding previous period cost
  3. Skips entries with zero previous cost (avoids noise)
  4. Calculates percentage change: `((current - previous) / previous) * 100`
  5. Flags spike if:
     - Percentage change > threshold **OR**
     - Current cost > absolute threshold
  6. Rounds values and appends to suspects list
  7. Returns all detected anomalies

---

### 5. `parser.py` - Response Parser
**Purpose**: Converts raw AWS API responses into usable data structures

**Function: `parse_cost_response(response)`**
- **Input**: Raw AWS Cost Explorer API response (JSON structure)
- **Output**: Dictionary with (service, region) tuples as keys and costs as values
  ```python
  {
    ("Amazon EC2", "us-east-1"): 1234.56,
    ("Amazon S3", "us-west-2"): 789.01
  }
  ```

- **Working**:
  1. Initializes empty costs dictionary
  2. Iterates through `ResultsByTime` array
  3. For each time bucket, loops through `Groups`
  4. Extracts service and region from `Keys`
  5. Extracts cost amount from `Metrics.UnblendedCost.Amount`
  6. Converts amount to float
  7. Uses (service, region) tuple as key
  8. Accumulates costs if same key appears multiple times
  9. Returns aggregated costs dictionary

---

### 6. `test_ce.py` - Testing Script
**Purpose**: Quick test to verify Cost Explorer API connectivity

**Working**:
- Initializes boto3 Cost Explorer client for us-east-1
- Fetches December 2025 cost data
- Groups by SERVICE and REGION
- Pretty-prints raw response for inspection
- **Note**: Uses December 2025 dates (may return empty results if run before that period)

---

## Input/Output Summary

### Overall System Input
- AWS credentials (via boto3 default credential chain)
- Configuration parameters in `config.py`

### Overall System Output
Example output from `agent.run()`:
```python
[
  {
    "service": "Amazon EC2",
    "region": "us-east-1",
    "current_cost": 1500.25,
    "previous_cost": 1000.00,
    "change_pct": 50.03,
    "time_window": "last_14_days"
  },
  {
    "service": "Amazon S3",
    "region": "us-west-2",
    "current_cost": 1200.00,
    "previous_cost": 800.00,
    "change_pct": 50.00,
    "time_window": "last_14_days"
  }
]
```

---

## Key Features

1. **Service & Region Granularity**: Tracks costs at service+region level for precise anomaly detection
2. **Dual Threshold Detection**: Uses both percentage-based and absolute thresholds
3. **Noise Filtering**: Ignores new services (zero previous cost) to reduce false positives
4. **Modular Design**: Separated concerns (client, parser, detector) for easy maintenance
5. **Configurable**: Easy parameter adjustment via `config.py`

---

## Usage

```python
from agent import run

# Run the detection agent
spikes = run()

# Process results
for spike in spikes:
    print(f"Alert: {spike['service']} in {spike['region']}")
    print(f"Cost increased by {spike['change_pct']}%")
    print(f"From ${spike['previous_cost']} to ${spike['current_cost']}")
```

---

## Prerequisites

- Python 3.x
- boto3 library
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)
- Cost Explorer API access enabled in AWS account

---

## Detection Logic

A cost spike is flagged when **either** condition is met:
1. **Percentage Spike**: Cost increased by more than 30% compared to previous period
2. **Absolute Spike**: Current cost exceeds $1000 regardless of change percentage

---

## Notes

- Cost Explorer operates in `us-east-1` region only (global service)
- Uses `UnblendedCost` metric (actual costs without reserved instance discounts)
- Monthly granularity aggregates all costs within the time period
- Empty previous costs are ignored to prevent division by zero and noise
