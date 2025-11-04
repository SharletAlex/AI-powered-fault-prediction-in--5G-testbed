"""
Data Preprocessing Pipeline for 5G Fault Prediction
Author: Data Engineer (Member 1)
Date: November 4, 2025 - Day 2

This script preprocesses the synthetic 5G dataset for machine learning:
- Cleans and validates data
- Handles categorical encoding
- Scales numeric features
- Splits into train/test sets (80/20)
- Saves processed datasets and artifacts
"""

import pandas as pd
import numpy as np
import pickle
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Configuration
RANDOM_STATE = 42
TEST_SIZE = 0.20
INPUT_FILE = '../data/synthetic_5g_fault_dataset.csv'
OUTPUT_TRAIN = '../data/train.csv'
OUTPUT_TEST = '../data/test.csv'
SCALER_FILE = '../data/scaler.pkl'
LABEL_ENCODER_FILE = '../data/label_encoder.pkl'

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"{title}")
    print("="*70)

def load_data(file_path):
    """Load the synthetic dataset"""
    print_section("1. LOADING DATA")
    print(f"Loading dataset from: {file_path}")
    
    df = pd.read_csv(file_path)
    print(f"✓ Dataset loaded successfully")
    print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    return df

def clean_data(df):
    """Clean and validate the dataset"""
    print_section("2. DATA CLEANING")
    
    initial_rows = len(df)
    
    # Check for missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"⚠️  Found {missing} missing values")
        df = df.dropna()
        print(f"✓ Dropped rows with missing values")
    else:
        print("✓ No missing values found")
    
    # Remove duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"⚠️  Found {duplicates} duplicate rows")
        df = df.drop_duplicates()
        print(f"✓ Removed duplicate rows")
    else:
        print("✓ No duplicates found")
    
    # Check for outliers (optional - just report)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_report = []
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        if outliers > 0:
            outlier_report.append(f"  {col}: {outliers} outliers")
    
    if outlier_report:
        print(f"\n📊 Outlier Detection (3×IQR method):")
        for report in outlier_report[:5]:  # Show first 5
            print(report)
        print(f"  Note: Outliers retained (may represent faulty conditions)")
    
    final_rows = len(df)
    print(f"\n✓ Cleaning complete: {initial_rows} → {final_rows} rows")
    
    return df

def prepare_features(df):
    """Prepare features for training"""
    print_section("3. FEATURE PREPARATION")
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print("✓ Converted timestamp to datetime format")
    
    # Identify feature types
    categorical_features = ['base_station_id', 'cell_id']
    temporal_features = ['timestamp']
    numeric_features = [col for col in df.columns 
                       if col not in categorical_features + temporal_features + ['fault_status']]
    
    print(f"\n📊 Feature Categories:")
    print(f"  Numeric features: {len(numeric_features)}")
    print(f"  Categorical features: {len(categorical_features)}")
    print(f"  Temporal features: {len(temporal_features)}")
    print(f"  Target variable: 1 (fault_status)")
    
    return df, numeric_features, categorical_features, temporal_features

def encode_features(df, categorical_features):
    """Encode categorical variables"""
    print_section("4. CATEGORICAL ENCODING")
    
    df_encoded = df.copy()
    
    # For base_station_id and cell_id, we'll use simple label encoding
    # In production, you might want to use one-hot encoding or embeddings
    for col in categorical_features:
        le = LabelEncoder()
        df_encoded[col + '_encoded'] = le.fit_transform(df_encoded[col])
        print(f"✓ Encoded {col}: {df_encoded[col].nunique()} unique values")
    
    # Encode target variable
    target_encoder = LabelEncoder()
    df_encoded['fault_status_encoded'] = target_encoder.fit_transform(df_encoded['fault_status'])
    
    # Save label encoder for target
    with open(LABEL_ENCODER_FILE, 'wb') as f:
        pickle.dump(target_encoder, f)
    print(f"\n✓ Target variable encoded: {dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))}")
    print(f"✓ Label encoder saved to: {LABEL_ENCODER_FILE}")
    
    return df_encoded, target_encoder

def scale_features(df, numeric_features):
    """Scale numeric features using StandardScaler"""
    print_section("5. FEATURE SCALING")
    
    df_scaled = df.copy()
    
    # Initialize scaler
    scaler = StandardScaler()
    
    # Fit and transform numeric features
    df_scaled[numeric_features] = scaler.fit_transform(df[numeric_features])
    
    # Save scaler
    with open(SCALER_FILE, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"✓ Scaled {len(numeric_features)} numeric features")
    print(f"✓ Scaler saved to: {SCALER_FILE}")
    
    # Show scaling statistics
    print(f"\n📊 Scaling Statistics (first 5 features):")
    for i, col in enumerate(numeric_features[:5]):
        print(f"  {col}:")
        print(f"    Mean: {scaler.mean_[i]:.4f} | Std: {scaler.scale_[i]:.4f}")
    
    return df_scaled, scaler

def split_data(df, numeric_features, categorical_features):
    """Split data into train and test sets"""
    print_section("6. TRAIN-TEST SPLIT")
    
    # Prepare feature columns (exclude original categorical and timestamp)
    feature_cols = numeric_features + [col + '_encoded' for col in categorical_features]
    
    X = df[feature_cols]
    y = df['fault_status_encoded']
    
    # Stratified split to maintain class balance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=TEST_SIZE, 
        random_state=RANDOM_STATE,
        stratify=y
    )
    
    print(f"✓ Split ratio: {int((1-TEST_SIZE)*100)}% train / {int(TEST_SIZE*100)}% test")
    print(f"\nTrain set:")
    print(f"  Samples: {len(X_train):,}")
    print(f"  Normal: {(y_train == 0).sum():,} ({(y_train == 0).sum()/len(y_train)*100:.2f}%)")
    print(f"  Faulty: {(y_train == 1).sum():,} ({(y_train == 1).sum()/len(y_train)*100:.2f}%)")
    
    print(f"\nTest set:")
    print(f"  Samples: {len(X_test):,}")
    print(f"  Normal: {(y_test == 0).sum():,} ({(y_test == 0).sum()/len(y_test)*100:.2f}%)")
    print(f"  Faulty: {(y_test == 1).sum():,} ({(y_test == 1).sum()/len(y_test)*100:.2f}%)")
    
    return X_train, X_test, y_train, y_test

def save_processed_data(X_train, X_test, y_train, y_test):
    """Save processed datasets"""
    print_section("7. SAVING PROCESSED DATA")
    
    # Combine features and target
    train_df = X_train.copy()
    train_df['fault_status'] = y_train.values
    
    test_df = X_test.copy()
    test_df['fault_status'] = y_test.values
    
    # Save to CSV
    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)
    
    print(f"✓ Train set saved to: {OUTPUT_TRAIN}")
    print(f"  Size: {len(train_df):,} samples")
    print(f"  Features: {len(train_df.columns) - 1}")
    
    print(f"\n✓ Test set saved to: {OUTPUT_TEST}")
    print(f"  Size: {len(test_df):,} samples")
    print(f"  Features: {len(test_df.columns) - 1}")
    
    # Calculate file sizes
    train_size = pd.read_csv(OUTPUT_TRAIN).memory_usage(deep=True).sum() / 1024 / 1024
    test_size = pd.read_csv(OUTPUT_TEST).memory_usage(deep=True).sum() / 1024 / 1024
    
    print(f"\n📊 File Sizes:")
    print(f"  train.csv: {train_size:.2f} MB")
    print(f"  test.csv: {test_size:.2f} MB")
    
    return train_df, test_df

def generate_summary(df_original, train_df, test_df, numeric_features):
    """Generate preprocessing summary"""
    print_section("8. PREPROCESSING SUMMARY")
    
    print("📊 Dataset Transformation:")
    print(f"  Original: {df_original.shape}")
    print(f"  Train: {train_df.shape}")
    print(f"  Test: {test_df.shape}")
    
    print(f"\n✓ Features Processed:")
    print(f"  Numeric features scaled: {len(numeric_features)}")
    print(f"  Categorical features encoded: 2")
    print(f"  Total features for ML: {len(train_df.columns) - 1}")
    
    print(f"\n✓ Artifacts Saved:")
    print(f"  1. train.csv - Training dataset")
    print(f"  2. test.csv - Testing dataset")
    print(f"  3. scaler.pkl - StandardScaler for deployment")
    print(f"  4. label_encoder.pkl - Target encoder for predictions")
    
    print(f"\n✓ Class Distribution (Maintained):")
    train_normal_pct = (train_df['fault_status'] == 0).sum() / len(train_df) * 100
    train_faulty_pct = (train_df['fault_status'] == 1).sum() / len(train_df) * 100
    test_normal_pct = (test_df['fault_status'] == 0).sum() / len(test_df) * 100
    test_faulty_pct = (test_df['fault_status'] == 1).sum() / len(test_df) * 100
    
    print(f"  Train: {train_normal_pct:.1f}% Normal / {train_faulty_pct:.1f}% Faulty")
    print(f"  Test:  {test_normal_pct:.1f}% Normal / {test_faulty_pct:.1f}% Faulty")

def main():
    """Main preprocessing pipeline"""
    print("="*70)
    print("5G FAULT PREDICTION - DATA PREPROCESSING PIPELINE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Load data
    df = load_data(INPUT_FILE)
    df_original = df.copy()
    
    # 2. Clean data
    df = clean_data(df)
    
    # 3. Prepare features
    df, numeric_features, categorical_features, temporal_features = prepare_features(df)
    
    # 4. Encode categorical features
    df, target_encoder = encode_features(df, categorical_features)
    
    # 5. Scale numeric features
    df, scaler = scale_features(df, numeric_features)
    
    # 6. Split data
    X_train, X_test, y_train, y_test = split_data(df, numeric_features, categorical_features)
    
    # 7. Save processed data
    train_df, test_df = save_processed_data(X_train, X_test, y_train, y_test)
    
    # 8. Generate summary
    generate_summary(df_original, train_df, test_df, numeric_features)
    
    # Final message
    print("\n" + "="*70)
    print("✅ PREPROCESSING COMPLETE!")
    print("="*70)
    print(f"\n🎯 Ready for ML Model Training!")
    print(f"📁 Training data: {OUTPUT_TRAIN}")
    print(f"📁 Testing data: {OUTPUT_TEST}")
    print(f"📁 Scaler: {SCALER_FILE}")
    print(f"📁 Encoder: {LABEL_ENCODER_FILE}")
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
