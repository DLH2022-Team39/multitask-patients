#!/usr/bin/env python3
import numpy as np
import pandas as pd

MIMIC_DIR = 'data/mimic-iii-clinical-database-1.4/'
    
# Variables used for prediction as stated in the paper
pred_vars = [
    'Anion gap',
    'Bicarbonate',
    'blood pH',
    'Blood urea nitrogen',
    'Chloride',
    'Creatinine',
    'Diastolic blood pressure',
    'Fraction inspired oxygen',
    'Glascow coma scale total',
    'Glucose',
    'Heart rate',
    'Hematocrit',
    'Hemoglobin',
    'INR',
    'Lactate',
    'Magnesium',
    'Mean blood pressure',
    'Oxygen saturation',
    'Partial thromboplastin time',
    'Phosphate',
    'Platelets',
    'Potassium',
    'Prothrombin time',
    'Respiratory rate',
    'Sodium',
    'Systolic blood pressure',
    'Temperature',
    'Weight',
    'White blood cell count',
]

# Lab tests the paper uses as predictive variables
labevents_items = [
    'Anion Gap',
    'Bicarbonate',
    'pH',
    'Urea Nitrogen',
    'Chloride',
    'Creatinine',
    'Glucose',
    'Hematocrit',
    'Hemoglobin',
    'Lactate',
    'Magnesium',
    'Oxygen Saturation',
    'Phosphate',
    'Platelet Clumps','Platelet Count','Platelet Smear',
    'Potassium',
    'Sodium',
    'WBC Count',
]

# Feature names in chartevents
chart_features = [
    'Hematocrit',
    'Hemoglobin',
    'Platelets',
    'Chloride',
    'Creatinine',
    'Glucose',
    'Magnesium',
    'Potassium',
    'Sodium',
    'Potassium',
    'Platelets',
    'Magnesium',
    'Platelets',
    'Anion gap',
    'Prothrombin time',
    'Creatinine',
    'Magnesium',
    'Hemoglobin',
    'Heart Rate',
    'INR',
    'Admission Weight (lbs.)',
    'Daily Weight',
    'Admission Weight (Kg)',
    'Respiratory Rate',
    'Heart Rate',
    'PH (Venous)',
    'BUN',
    'GCS Total',
    'Phosphorous',
    'Lactic Acid'
    'Non Invasive Blood Pressure diastolic',
    'Arterial Blood Pressure diastolic',
    'Pulmonary Artery Pressure diastolic',
    'ART BP Diastolic',
    'Manual Blood Pressure Diastolic Left',
    'Manual Blood Pressure Diastolic Right',
    'Aortic Pressure Signal - Diastolic',
    'Temperature Fahrenheit',
    'Temperature Celsius'
    'Arterial Blood Pressure systolic',
    'Pulmonary Artery Pressure systolic',
    'Non Invasive Blood Pressure systolic',
    'ART BP Systolic',
    'O2 saturation pulseoxymetry',
    'Prothrombin time',
    'WBC',
    'Inspired O2 Fraction',
    'Arterial Blood Pressure mean',
    'Non Invasive Blood Pressure mean',
    'ART BP mean',
    'Arterial CO2 Pressure',
    'TCO2 (calc) Arterial',
    'TCO2 (calc) Venous',
    'Venous CO2 Pressure',
]


def get_charts(nrows=None):
    def get_item_map():
        d_items = pd.read_csv(MIMIC_DIR + 'D_ITEMS.csv.gz')
        item_map = d_items.set_index('ITEMID')['LABEL'].to_dict()
        item_map = { x[0]:x[1] for x in item_map.items() \
                if isinstance(x[1],str) }
        return item_map


    # Read chartevents
    charts_types = {
        "SUBJECT_ID": np.int32,
        "HADM_ID": np.int32,
        "ICUSTAY_ID": np.float32,
        "ITEMID": np.int32,
        "CGID": np.float32,
        # "VALUE": float,
        "VALUENUM": np.float32,
        "WARNING": np.float32,
        "ERROR": np.float32,
    }
    charts_times = ["CHARTTIME"]
    usecols = list(charts_types.keys()) + charts_times
    charts = pd.read_csv(MIMIC_DIR + 'CHARTEVENTS.csv.gz', 
            dtype=charts_types, parse_dates=charts_times, nrows=nrows,
            usecols=usecols)

    # Filter for only chart events the paper uses
    item_map = get_item_map()
    chart_feature_keys = [k for k,v in item_map.items() if v in chart_features]
    charts = charts.loc[charts.ITEMID.isin(chart_feature_keys),:]
    
    # Lower the column names to match the paper's code
    charts.columns = [x.lower() for x in charts.columns]
   
    # Create hours_in feature
    icustays = pd.read_csv(MIMIC_DIR + 'ICUSTAYS.csv.gz', 
            parse_dates=['INTIME'])
    charts = charts.join(icustays.groupby('SUBJECT_ID')['INTIME'].min(), 
            on='subject_id')
    charts['hours_in'] = charts.charttime-charts.INTIME
    charts['hours_in'] = charts['hours_in'] / np.timedelta64(1, 'h')
    charts['hours_in'] = charts['hours_in'].round()
    
    # Drop rows corresponding to previous stays
    charts = charts.loc[charts.hours_in>0]
    charts.hours_in = charts.hours_in.astype(np.int32)
    
    # Drop unused and reorder
    INDEX_COLS = ['subject_id', 'icustay_id', 'hours_in', 'hadm_id']
    other_cols = [x for x in charts.columns if x not in INDEX_COLS]
    cols = INDEX_COLS + other_cols
    charts = charts[cols]

    
    # Average all measurements per subject per stay per lab test per hour
    charts = charts.groupby(
            ['subject_id','icustay_id', 'hours_in','hadm_id','itemid']).mean()
    
    # Convert column multindex to flat
    charts = charts.unstack()
    charts.columns = ['_'.join([str(y) for y in x]) for \
            x in charts.columns.to_flat_index()]
    charts = charts.reset_index()
    return charts


def get_labevents():
    # Read labevents
    labitems_types = {
        "SUBJECT_ID": np.int32,
        "HADM_ID": np.float32,
        "ITEMID": np.int32,
        "VALUE": str,
        "VALUENUM": np.float32,
    }
    labitems_times = ["CHARTTIME"]
    usecols = list(labitems_types.keys()) + labitems_times
    labevents = pd.read_csv(MIMIC_DIR + 'LABEVENTS.csv.gz',
            dtype=labitems_types, parse_dates=labitems_times,
            usecols=usecols)
    
    # Add labitem description
    d_labitems = pd.read_csv(MIMIC_DIR + 'D_LABITEMS.csv.gz')
    lab_map = d_labitems.set_index('ITEMID')['LABEL'].to_dict()
    lab_item_nums = [k for k,v in lab_map.items() if v in labevents_items]

    # Filter only relevant lab_items
    labevents[labevents.ITEMID.isin(lab_item_nums)]

    # Create hours_in column
    icustays = pd.read_csv(MIMIC_DIR + 'ICUSTAYS.csv.gz', 
            parse_dates=['INTIME'])
    labevents = labevents.join(icustays.groupby('SUBJECT_ID')['INTIME'].min(),
            on='SUBJECT_ID')
    labevents['hours_in'] = labevents.CHARTTIME-labevents.INTIME
    labevents['hours_in'] = labevents['hours_in'] / np.timedelta64(1, 'h')
    labevents['hours_in'] = labevents['hours_in'].round()
    labevents = labevents.drop(columns=['INTIME', 'CHARTTIME'])

    # Drop rows corresponding to previous stays
    labevents = labevents.loc[labevents.hours_in>0]
    labevents.hours_in = labevents.hours_in.astype(np.int32)

    # Average all measurements per subject per stay per lab test per hour
    labevents = labevents.groupby(
            ['SUBJECT_ID', 'hours_in','HADM_ID','ITEMID']).mean()

    # Convert column multindex to flat
    labevents = labevents.unstack()
    labevents.columns = ['_'.join([str(y) for y in x]) for \
            x in labevents.columns.to_flat_index()]
    labevents = labevents.reset_index()
    
    # Lower the column names to match the paper's code
    labevents.columns = [x.lower() for x in labevents.columns]
    return labevents


def get_static():
    # Read admissions data
    admissions_cols = ['ETHNICITY', 'DEATHTIME', 'DISCHTIME']
    admissions = pd.read_csv(MIMIC_DIR + 'ADMISSIONS.csv.gz')
    admissions = admissions.set_index('SUBJECT_ID')[admissions_cols]
    
    # Read patients data
    patients_cols = ['GENDER', 'DOB']
    patients = pd.read_csv(MIMIC_DIR + 'PATIENTS.csv.gz', parse_dates=['DOB'])
    patients = patients.set_index('SUBJECT_ID')[patients_cols]

    # Read icustay data
    icustays_cols = ['HADM_ID', 'ICUSTAY_ID', 'FIRST_CAREUNIT', 'INTIME']
    icustays = pd.read_csv(MIMIC_DIR + 'ICUSTAYS.csv.gz',
            parse_dates=['INTIME'])
    icustays = icustays.set_index('SUBJECT_ID')[icustays_cols]

    # Join tables on subject_id
    static = icustays.join(admissions,how='left').join(patients, how='left')
    static = static.reset_index().drop_duplicates()

    # Sort by subject_id, intime, and drop all but first hospital stay
    # as stated in the paper
    static = static.sort_values(by=['SUBJECT_ID', 'INTIME'])
    static = static.drop_duplicates(subset='SUBJECT_ID', keep='first')

    # Calculate age
    static['AGE'] = static.INTIME.subtract(static['DOB']).dt.days / 365

    # Lower the column names to match the paper's code
    static.columns = [x.lower() for x in static.columns]
    return static


def make_X(static, nrows=None):
    charts = get_charts(nrows=nrows)
    labevents = get_labevents()

    # Join charts and labevents dataframes on subject, hours_in
    labevents = labevents.set_index(['subject_id','hours_in','hadm_id'])
    X = charts.set_index(
            ['subject_id','icustay_id', 'hours_in','hadm_id']).join(labevents)

    # Drop columns with all NA's and reset index
    X = X.dropna(axis=1,how='all').reset_index()
    
    # Convert to smaller width on some columns
    cols = ['subject_id', 'hours_in', 'hadm_id', 'icustay_id']
    for col in cols:
        X[col] = X[col].astype(np.int32)

    # Drop patients less than 15 years of age as stated in the paper
    X = X.set_index(cols).join(
            static.set_index(['subject_id','icustay_id', 'hadm_id'])['age'])
    X = X[X.age>=15].drop(columns='age')

    # Write out
    X.to_hdf('data/X.h5', key='X', mode='w')


if __name__ == "__main__":
    static = get_static()
    static.to_csv('data/static.csv', index=False)
    make_X(static, nrows=100_000_000)

