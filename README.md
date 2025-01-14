# DVH Meteric Calculator

## Overview
**DVH Calculator** is a Streamlit-based web application designed to analyze Dose-Volume Histogram (DVH) data. The app computes key dose and volume metrics (`Dcc`, `D%`, `Vcc`, and `V%`) and identifies high-risk patient groups based on clinical thresholds.

## Features
- **Dose Metrics Calculation**
  - `Dcc` Metrics: Dose corresponding to a specific volume (e.g., `D10cc`, `D20cc`)
  - `D%` Metrics: Dose corresponding to a percentage of total volume (e.g., `D2%`, `D10%`)
  - `Vcc` Metrics: Volume corresponding to a specific dose (e.g., `V60Gy`)
  - `V%` Metrics: Percentage of volume at a specific dose

- **High-Risk Group Identification**
  - Flags patients as high risk if:
    - `D10cc(Gy) > 59.2`
    - `V60Gy(cc) > 12.44`

- **Interactive Data Display**
  - Visualizes computed metrics in dynamic tables  
  - Provides real-time risk assessment notifications

- **File Format Support**
  - Accepts **CSV** and **Excel** files (`.xls`, `.xlsx`)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/fmhr12/dvh-calculator.git
   cd dvh-calculator
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
3. **Run the Application**
   ```bash
   streamlit run app.py

