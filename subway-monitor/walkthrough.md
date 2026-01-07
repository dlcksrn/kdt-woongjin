# Subway Monitor - Verification Walkthrough

The project has been successfully set up, and the data collector is functional.

## Accomplishments

1.  **Project Structure**: Created `subway-monitor` directory with necessary scripts.
2.  **Database Connection**: Configured connection to Supabase (PostgreSQL) using Connection Pooler (IPv4).
3.  **Schema Initialization**: Created `realtime_train_positions` table with English column names.
4.  **Data Collection**: Implemented `collector.py` to fetch data from Seoul Open Data API and store it in the database.

## Verification Results

### 1. Database Initialization
Ran `init_db.py` to create the table.
> Output: `Database schema initialized successfully.`

### 2. Data Collection Test
Ran `collector.py` to fetch real-time data.
> Result: Validated that data was fetched for lines (1호선, 2호선, etc.) and inserted.

### 3. Data Storage Verification
Checked the row count in the database.
> **Total Rows**: `824` (at time of verification)

## How to Run

### Manual Collection (One-time)
```bash
cd subway-monitor
venv\Scripts\activate
python -c "import collector; collector.job()"
```

### Continuous Monitoring
The script is designed to run continuously using `schedule`.
```bash
python collector.py
```
*   This will fetch data every **1 minute** (default setting).

## Next Steps (Analysis)
Now that data is flowing, you can proceed with the analysis goals:
1.  **Headway Monitoring**: Query `received_at` differences by station.
2.  **Dwell Time**: Analyze arrival vs. departure status events.
3.  **Express Impact**: Compare local train delays after express trains.
