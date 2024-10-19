import streamlit as st
import pandas as pd
import numpy as np
import os
import openpyxl 

# Define the volume metrics (Dcc and D%)
Dcc_values = {
            "D0.035cc": 0.035,
            "D0.1cc": 0.1,
            "D0.5cc": 0.5,
            "D2cc": 2,
            "D5cc": 5,
            "D10cc": 10,
            "D15cc": 15,
            "D20cc": 20,
            "D25cc": 25,
            "D30cc": 30,
            "D35cc": 35,
            "D40cc": 40,
            "D45cc": 45,
            "D50cc": 50,
            "D55cc": 55,
            "D60cc": 60,
            "D65cc": 65,
            "D70cc": 70,
            "D75cc": 75,
            "D80cc": 80,
            "D85cc": 85,
            "D90cc": 90,
            "D95cc": 95,
            "D100cc": 100,
        }

D_percent_values = {
            "D2%": 0.02,
            "D5%": 0.05,
            "D10%": 0.10,
            "D15%": 0.15,
            "D20%": 0.20,
            "D25%": 0.25,
            "D30%": 0.30,
            "D35%": 0.35,
            "D40%": 0.40,
            "D45%": 0.45,
            "D50%": 0.50,
            "D55%": 0.55,
            "D60%": 0.60,
            "D65%": 0.65,
            "D70%": 0.70,
            "D75%": 0.75,
            "D80%": 0.80,
            "D85%": 0.85,
            "D90%": 0.90,
            "D95%": 0.95,
            "D97%": 0.97,
            "D98%": 0.98,
            "D99%": 0.99
        }
        # Define the doses for volume calculation (Vcc and V%)
doses = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000]
        
def process_excel(uploaded_file):
    try:
        # Create a pandas ExcelFile object from the uploaded file
        xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
        sheet_names = xls.sheet_names

        # Extract filename
        filename = uploaded_file.name
        patient_number = os.path.splitext(filename)[0]
        st.write(f"**Processing file:** {filename}")

        # Initialize dictionaries to collect all results
        Dcc_metrics = {}
        D_percent_metrics = {}
        Vcc_metrics = {}
        V_percent_metrics = {}



        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            df = df.fillna(0)

            # Calculate Dcc metrics
            for metric, volume in Dcc_values.items():
                volume_difference = np.abs(df.iloc[1:, 1:].values - volume)
                if volume_difference.size == 0:
                    st.warning(f"No data found in sheet '{sheet_name}' for metric '{metric}'. Skipping.")
                    continue
                row, col = np.unravel_index(np.argmin(volume_difference), volume_difference.shape)
                dose_row = df.iat[row + 1, 0]
                dose_col = df.iat[0, col + 1]
                try:
                    dose = int(dose_row + dose_col)
                except (ValueError, TypeError):
                    st.warning(f"Non-integer dose values found in sheet '{sheet_name}' for metric '{metric}'. Skipping.")
                    continue
                # Format the metric name with (Gy) suffix
                formatted_metric = f"{metric}(Gy)"
                Dcc_metrics[formatted_metric] = dose / 100  # Convert cGy to Gy

            # Calculate D% metrics
            if df.shape[0] > 1 and df.shape[1] > 1:
                total_volume = df.iat[1, 1]  # Assuming this is the total volume
            else:
                total_volume = 0
                st.warning(f"Insufficient data in sheet '{sheet_name}' to calculate total volume.")

            for metric, percentage in D_percent_values.items():
                if total_volume == 0:
                    D_percent_metrics[f"{metric}(Gy)"] = np.nan
                    continue
                volume_threshold = percentage * total_volume
                volume_difference = np.abs(df.iloc[1:, 1:].values - volume_threshold)
                if volume_difference.size == 0:
                    st.warning(f"No data found in sheet '{sheet_name}' for metric '{metric}'. Skipping.")
                    continue
                row, col = np.unravel_index(np.argmin(volume_difference), volume_difference.shape)
                dose_row = df.iat[row + 1, 0]
                dose_col = df.iat[0, col + 1]
                try:
                    dose = int(dose_row + dose_col)
                except (ValueError, TypeError):
                    st.warning(f"Non-integer dose values found in sheet '{sheet_name}' for metric '{metric}'. Skipping.")
                    continue
                # Format the metric name with (Gy) suffix
                formatted_metric = f"{metric}(Gy)"
                D_percent_metrics[formatted_metric] = dose / 100  # Convert cGy to Gy

            # Calculate Vcc and V% metrics
            try:
                header = df.iloc[0, 1:].astype(float)  # Dose increments from the first row, excluding the first cell
                index = df.iloc[1:, 0].astype(float)    # Base doses from the first column, excluding the first cell
            except ValueError:
                st.warning(f"Non-numeric data found in headers or index of sheet '{sheet_name}'. Skipping V metrics.")
                continue

            for dose in doses:
                dose_diff = np.abs(index.values[:, None] + header.values - dose)
                if dose_diff.size == 0:
                    st.warning(f"No data found in sheet '{sheet_name}' for dose '{dose}'. Skipping.")
                    continue
                row, col = np.unravel_index(np.argmin(dose_diff), dose_diff.shape)
                try:
                    volume = df.iloc[row + 1, col + 1]
                except IndexError:
                    st.warning(f"Index out of bounds for dose '{dose}' in sheet '{sheet_name}'. Skipping.")
                    continue
                dose_str = f'V{int(dose / 100)}Gy'
                # Format the metric names
                Vcc_metric = f"{dose_str}(cc)"
                V_percent_metric = f"{dose_str}(%)"
                Vcc_metrics[Vcc_metric] = volume
                if total_volume > 0:
                    V_percent_metrics[V_percent_metric] = round((volume / total_volume) * 100, 1)
                else:
                    V_percent_metrics[V_percent_metric] = np.nan

        # Create separate DataFrames for each metric type
        Dcc_df = pd.DataFrame([Dcc_metrics])
        Dcc_df.index = ['Dcc']

        D_percent_df = pd.DataFrame([D_percent_metrics])
        D_percent_df.index = ['D%']

        Vcc_df = pd.DataFrame([Vcc_metrics])
        Vcc_df.index = ['Vcc']

        V_percent_df = pd.DataFrame([V_percent_metrics])
        V_percent_df.index = ['V%']

        # Display the results
        st.write("## Dcc(Gy) Metrics")
        st.dataframe(Dcc_df)

        st.write("## D%(Gy) Metrics")
        st.dataframe(D_percent_df)

        st.write("## VGy(cc) Metrics")
        st.dataframe(Vcc_df)

        st.write("## VGy(%) Metrics")
        st.dataframe(V_percent_df)

        # High-Risk Group Checks
        high_risk_messages = []

        # Check D10cc(Gy) > 59.2
        if 'D10cc(Gy)' in Dcc_df.columns:
            d10cc_value = Dcc_df.at['Dcc', 'D10cc(Gy)']
            if pd.notnull(d10cc_value) and d10cc_value > 59.2:
                high_risk_messages.append("Patient is in high risk group (D10cc(Gy) > 59.2).")

        # Check V60Gy(cc) > 12.6
        if 'V60Gy(cc)' in Vcc_df.columns:
            v60cc_value = Vcc_df.at['Vcc', 'V60Gy(cc)']
            if pd.notnull(v60cc_value) and v60cc_value > 12.6:
                high_risk_messages.append("Patient is in high risk group (V60Gy(cc) > 12.6).")

        # Display high-risk messages if any
        if high_risk_messages:
            st.write("## High-Risk Group Notifications")
            for message in high_risk_messages:
                st.warning(message)
        else:
            st.write("## High-Risk Group Notifications")
            st.success("Patient does not meet any high-risk criteria based on D10cc(Gy) and V60Gy(cc).")

    except FileNotFoundError:
        st.error(f"The file '{uploaded_file.name}' does not exist. Please check the file and try again.")
    except Exception as e:
        st.error(f"An error occurred while processing the Excel file: {e}")

def process_csv(csv_file):
    try:
        # Extract filename
        filename = csv_file.name
        patient_number = os.path.splitext(filename)[0]
        st.write(f"**Processing file:** {filename}")

        # Initialize dictionaries to collect all results
        Dcc_metrics = {}
        D_percent_metrics = {}
        Vcc_metrics = {}
        V_percent_metrics = {}

        # Read the CSV file
        df = pd.read_csv(csv_file, header=None)
        if df.empty:
            st.error("The uploaded CSV file is empty.")
            return

        df = df.fillna(0)

        # Calculate Dcc metrics
        for metric, volume in Dcc_values.items():
            volume_difference = np.abs(df.iloc[1:, 1:].values - volume)
            if volume_difference.size == 0:
                st.warning(f"No data found for metric '{metric}'. Skipping.")
                continue
            row, col = np.unravel_index(np.argmin(volume_difference), volume_difference.shape)
            dose_row = df.iat[row + 1, 0]
            dose_col = df.iat[0, col + 1]
            try:
                dose = int(dose_row + dose_col)
            except (ValueError, TypeError):
                st.warning(f"Non-integer dose values found for metric '{metric}'. Skipping.")
                continue
            # Format the metric name with (Gy) suffix
            formatted_metric = f"{metric}(Gy)"
            Dcc_metrics[formatted_metric] = dose / 100  # Convert cGy to Gy

        # Calculate D% metrics
        if df.shape[0] > 1 and df.shape[1] > 1:
            total_volume = df.iat[1, 1]  # Assuming this is the total volume
        else:
            total_volume = 0
            st.warning("Insufficient data to calculate total volume.")

        for metric, percentage in D_percent_values.items():
            if total_volume == 0:
                D_percent_metrics[f"{metric}(Gy)"] = np.nan
                continue
            volume_threshold = percentage * total_volume
            volume_difference = np.abs(df.iloc[1:, 1:].values - volume_threshold)
            if volume_difference.size == 0:
                st.warning(f"No data found for metric '{metric}'. Skipping.")
                continue
            row, col = np.unravel_index(np.argmin(volume_difference), volume_difference.shape)
            dose_row = df.iat[row + 1, 0]
            dose_col = df.iat[0, col + 1]
            try:
                dose = int(dose_row + dose_col)
            except (ValueError, TypeError):
                st.warning(f"Non-integer dose values found for metric '{metric}'. Skipping.")
                continue
            # Format the metric name with (Gy) suffix
            formatted_metric = f"{metric}(Gy)"
            D_percent_metrics[formatted_metric] = dose / 100  # Convert cGy to Gy

        # Calculate Vcc and V% metrics
        try:
            header = df.iloc[0, 1:].astype(float)  # Dose increments from the first row, excluding the first cell
            index = df.iloc[1:, 0].astype(float)    # Base doses from the first column, excluding the first cell
        except ValueError:
            st.warning("Non-numeric data found in headers or index. Skipping V metrics.")
            header = pd.Series(dtype=float)
            index = pd.Series(dtype=float)

        for dose in doses:
            dose_diff = np.abs(index.values[:, None] + header.values - dose)
            if dose_diff.size == 0:
                st.warning(f"No data found for dose '{dose}'. Skipping.")
                continue
            row, col = np.unravel_index(np.argmin(dose_diff), dose_diff.shape)
            try:
                volume = df.iloc[row + 1, col + 1]
            except IndexError:
                st.warning(f"Index out of bounds for dose '{dose}'. Skipping.")
                continue
            dose_str = f'V{int(dose / 100)}Gy'
            # Format the metric names
            Vcc_metric = f"{dose_str}(cc)"
            V_percent_metric = f"{dose_str}(%)"
            Vcc_metrics[Vcc_metric] = volume
            if total_volume > 0:
                V_percent_metrics[V_percent_metric] = round((volume / total_volume) * 100, 1)
            else:
                V_percent_metrics[V_percent_metric] = np.nan

        # Create separate DataFrames for each metric type
        Dcc_df = pd.DataFrame([Dcc_metrics])
        Dcc_df.index = ['Dcc']

        D_percent_df = pd.DataFrame([D_percent_metrics])
        D_percent_df.index = ['D%']

        Vcc_df = pd.DataFrame([Vcc_metrics])
        Vcc_df.index = ['Vcc']

        V_percent_df = pd.DataFrame([V_percent_metrics])
        V_percent_df.index = ['V%']

        # Display the results
        st.write("## Dcc(Gy) Metrics")
        st.dataframe(Dcc_df)

        st.write("## D%(Gy) Metrics")
        st.dataframe(D_percent_df)

        st.write("## VGy(cc) Metrics")
        st.dataframe(Vcc_df)

        st.write("## VGy(%) Metrics")
        st.dataframe(V_percent_df)

        # High-Risk Group Checks
        high_risk_messages = []

        # Check D10cc(Gy) > 59.2
        if 'D10cc(Gy)' in Dcc_df.columns:
            d10cc_value = Dcc_df.at['Dcc', 'D10cc(Gy)']
            if pd.notnull(d10cc_value) and d10cc_value > 59.2:
                high_risk_messages.append("Patient is in high risk group (D10cc(Gy) > 59.2).")

        # Check V60Gy(cc) > 12.6
        if 'V60Gy(cc)' in Vcc_df.columns:
            v60cc_value = Vcc_df.at['Vcc', 'V60Gy(cc)']
            if pd.notnull(v60cc_value) and v60cc_value > 12.6:
                high_risk_messages.append("Patient is in high risk group (V60Gy(cc) > 12.6).")

        # Display high-risk messages if any
        if high_risk_messages:
            st.write("## High-Risk Group Notifications")
            for message in high_risk_messages:
                st.warning(message)
        else:
            st.write("## High-Risk Group Notifications")
            st.success("Patient does not meet any high-risk criteria based on D10cc(Gy) and V60Gy(cc).")

    except pd.errors.EmptyDataError:
        st.error("The uploaded Excel file is empty. Please upload a valid Excel file.")
    except pd.errors.ParserError:
        st.error("Error parsing the Excel file. Please ensure it is properly formatted.")
    except Exception as e:
        st.error(f"An error occurred while processing the Excel file: {e}")


def main():
    st.title("DVH Calculator")
    st.write("""
        Upload a CSV or Excel file to calculate Dcc(Gy), D%(Gy), VGy(cc), and VGy(%) metrics.
        
        The app will also notify if the patient is in a high-risk group based on the specified criteria.
    """)

    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])

    if uploaded_file is not None:
        # Determine the file type
        file_details = {
            "Filename": uploaded_file.name,
            "File Type": uploaded_file.type,
            "File Size": f"{uploaded_file.size} bytes"
        }

        # Reset the file pointer to the beginning
        uploaded_file.seek(0)

        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            try:
                process_excel(uploaded_file)
            except Exception as e:
                st.error(f"An error occurred while processing the Excel file: {e}")
        elif uploaded_file.name.endswith('.csv'):
            try:
                process_csv(uploaded_file)
            except Exception as e:
                st.error(f"An error occurred while processing the CSV file: {e}")
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")

if __name__ == "__main__":
    main()
