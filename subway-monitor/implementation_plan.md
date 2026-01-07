# Implementation Plan - Seoul Subway Real-time Monitoring

To build a data pipeline and analysis system for Seoul Subway Real-time Train Positions.

## User Review Required

> [!IMPORTANT]
> **Database Schema**: Please review the proposed column names in the Schema section to ensure they meet your preference for clarity.

## Proposed Changes

### Project Structure
Create a new directory `subway-monitor` in `kdt-woongjin`.

```
kdt-woongjin/
└── subway-monitor/
    ├── collector.py       # Script to fetch API and insert to DB
    ├── config.py          # Configuration (API Keys, DB URL)
    └── schema.sql         # SQL to create tables
```

### Database Schema (Supabase/Postgres)

Table Name: `realtime_train_positions`

| API Field | Column Name | Type | Description |
| :--- | :--- | :--- | :--- |
| subwayId | `subway_line_id` | VARCHAR | Line ID (e.g., 1001) |
| subwayNm | `subway_line_name` | VARCHAR | Line Name (e.g., 1호선) |
| statnId | `station_id` | VARCHAR | Current Station ID |
| statnNm | `station_name` | VARCHAR | Current Station Name |
| trainNo | `train_number` | VARCHAR | Train Number |
| lastRecptnDt | `last_received_at` | TIMESTAMPTZ | Final Reception Date |
| recptnDt | `received_at` | TIMESTAMPTZ | Reception Time |
| updnLine | `up_down_type` | INTEGER | 0: Up/Inner, 1: Down/Outer |
| statnTid | `terminal_station_id` | VARCHAR | Destination Station ID |
| statnTnm | `terminal_station_name` | VARCHAR | Destination Station Name |
| trainSttus | `train_status` | INTEGER | 0:Entry, 1:Arrive, 2:Depart, 3:Pre-depart |
| directAt | `is_express` | INTEGER | 0:No, 1:Express, 7:Special |
| lstcarAt | `is_last_train` | BOOLEAN | 1:Yes, 0:No |
| (Derived) | `created_at` | TIMESTAMPTZ | Record insertion time (Default NOW()) |

### Data Analysis Projects

**Goal**: Monitor for smooth subway operations.

1.  **Interval Regularity Analysis (Headway Monitoring)**
    *   **Purpose**: Detect signaling issues or delays by monitoring the time gap between trains at specific stations.
    *   **Method**: Group by `station_id` and `up_down_type`. Calculate `received_at` delta between consecutive `train_number` arrivals (`target_status=1`).
    *   **Metric**: Headway Variance (High variance = irregular operations).

2.  **Dwell Time Analysis**
    *   **Purpose**: Identify stations where trains stay longer than expected (potential congestion points).
    *   **Method**: For a specific `train_number`, calculate time difference between `train_status=1` (Arrival) and `train_status=2` (Departure) at the same `station_id`.

3.  **Express Train Impact Analysis**
    *   **Purpose**: Analyze if express trains (`is_express=1`) cause delays to local trains following them.
    *   **Method**: Correlate the headway of a local train immediately following an express train versus a local train following another local train.

4.  **Terminal Station Efficiency**
    *   **Purpose**: Optimize dispatching by analyzing the distribution of `terminal_station_name` during peak vs. off-peak hours.
    *   **Method**: Histogram of `terminal_station_name` over time of day.

## Verification Plan

### Automated Tests
*   **API Response Test**: Run a script to fetch one batch of data from the mock/real API URL and verify keys exist.
*   **DB Connection Test**: Verify connection to Supabase (using a placeholder URL/mock for now if credentials aren't provided).

### Manual Verification
*   **Run Collector**: Execute `python collector.py` and check console output for success message.
*   **Review Data**: If DB is connected, Query `SELECT * FROM realtime_train_positions LIMIT 5;`
