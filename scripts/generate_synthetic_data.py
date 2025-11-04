"""
Synthetic 5G Testbed Fault Dataset Generator
Author: Data Engineer (Member 1)
Date: November 4, 2025

This script generates synthetic data simulating 5G testbed network parameters
and labels data points as Normal or Faulty based on defined thresholds.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_SAMPLES = 10000
START_DATE = datetime(2025, 1, 1)

# 5G Network Parameter Ranges and Thresholds
NETWORK_PARAMS = {
    'rssi': {
        'normal_range': (-70, -50),      # dBm - Good signal strength
        'faulty_range': (-110, -90),     # dBm - Poor signal strength
        'threshold': -85                  # Below this is considered problematic
    },
    'sinr': {
        'normal_range': (15, 30),        # dB - Good signal quality
        'faulty_range': (-5, 5),         # dB - Poor signal quality
        'threshold': 10                   # Below this is considered problematic
    },
    'throughput': {
        'normal_range': (80, 150),       # Mbps - Good data rate
        'faulty_range': (10, 40),        # Mbps - Poor data rate
        'threshold': 50                   # Below this is considered problematic
    },
    'latency': {
        'normal_range': (5, 20),         # ms - Low latency
        'faulty_range': (80, 200),       # ms - High latency
        'threshold': 50                   # Above this is considered problematic
    },
    'jitter': {
        'normal_range': (1, 5),          # ms - Low variation
        'faulty_range': (20, 50),        # ms - High variation
        'threshold': 15                   # Above this is considered problematic
    },
    'packet_loss': {
        'normal_range': (0, 1),          # % - Minimal loss
        'faulty_range': (5, 20),         # % - Significant loss
        'threshold': 3                    # Above this is considered problematic
    }
}

def generate_timestamp(index, start_date):
    """Generate timestamp with 1-minute intervals"""
    return start_date + timedelta(minutes=index)

def generate_network_data(num_samples, fault_probability=0.3):
    """
    Generate synthetic 5G network data with realistic correlations
    
    Parameters:
    - num_samples: Number of data points to generate
    - fault_probability: Probability of generating a faulty record
    
    Returns:
    - DataFrame with network parameters and fault labels
    """
    
    data = []
    
    for i in range(num_samples):
        # Determine if this sample should be faulty
        is_faulty = random.random() < fault_probability
        
        # Generate base station and cell IDs
        base_station_id = f"BS_{random.randint(1, 50):03d}"
        cell_id = f"CELL_{random.randint(1, 200):04d}"
        
        # Generate timestamp
        timestamp = generate_timestamp(i, START_DATE)
        
        if is_faulty:
            # Generate faulty data with correlated parameters
            rssi = np.random.uniform(*NETWORK_PARAMS['rssi']['faulty_range'])
            sinr = np.random.uniform(*NETWORK_PARAMS['sinr']['faulty_range'])
            throughput = np.random.uniform(*NETWORK_PARAMS['throughput']['faulty_range'])
            latency = np.random.uniform(*NETWORK_PARAMS['latency']['faulty_range'])
            jitter = np.random.uniform(*NETWORK_PARAMS['jitter']['faulty_range'])
            packet_loss = np.random.uniform(*NETWORK_PARAMS['packet_loss']['faulty_range'])
            
            # Add some noise and occasional edge cases
            if random.random() < 0.2:  # 20% extreme cases
                rssi -= random.uniform(5, 15)
                latency += random.uniform(50, 100)
                packet_loss += random.uniform(5, 10)
        else:
            # Generate normal data
            rssi = np.random.uniform(*NETWORK_PARAMS['rssi']['normal_range'])
            sinr = np.random.uniform(*NETWORK_PARAMS['sinr']['normal_range'])
            throughput = np.random.uniform(*NETWORK_PARAMS['throughput']['normal_range'])
            latency = np.random.uniform(*NETWORK_PARAMS['latency']['normal_range'])
            jitter = np.random.uniform(*NETWORK_PARAMS['jitter']['normal_range'])
            packet_loss = np.random.uniform(*NETWORK_PARAMS['packet_loss']['normal_range'])
            
            # Add small random variations
            rssi += np.random.normal(0, 2)
            sinr += np.random.normal(0, 1)
            throughput += np.random.normal(0, 5)
        
        # Add additional contextual features
        cpu_usage = random.uniform(20, 95) if is_faulty else random.uniform(20, 70)
        memory_usage = random.uniform(40, 95) if is_faulty else random.uniform(30, 75)
        active_users = random.randint(50, 500) if not is_faulty else random.randint(500, 1000)
        temperature = random.uniform(45, 85) if is_faulty else random.uniform(25, 50)
        
        # Create record
        record = {
            'timestamp': timestamp,
            'base_station_id': base_station_id,
            'cell_id': cell_id,
            'rssi_dbm': round(rssi, 2),
            'sinr_db': round(sinr, 2),
            'throughput_mbps': round(throughput, 2),
            'latency_ms': round(latency, 2),
            'jitter_ms': round(jitter, 2),
            'packet_loss_percent': round(packet_loss, 2),
            'cpu_usage_percent': round(cpu_usage, 2),
            'memory_usage_percent': round(memory_usage, 2),
            'active_users': active_users,
            'temperature_celsius': round(temperature, 2),
            'fault_status': 'Faulty' if is_faulty else 'Normal'
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def add_derived_features(df):
    """Add derived features for better ML model performance"""
    
    # Time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_peak_hour'] = df['hour'].apply(lambda x: 1 if 9 <= x <= 17 else 0)
    
    # Network quality score (composite metric)
    df['network_quality_score'] = (
        (df['rssi_dbm'] + 100) / 50 * 0.2 +  # Normalize RSSI
        df['sinr_db'] / 30 * 0.2 +            # Normalize SINR
        df['throughput_mbps'] / 150 * 0.2 +   # Normalize throughput
        (100 - df['latency_ms']) / 100 * 0.2 + # Inverse latency
        (100 - df['packet_loss_percent']) / 100 * 0.2  # Inverse packet loss
    )
    df['network_quality_score'] = df['network_quality_score'].clip(0, 1)
    
    # Resource utilization indicator
    df['resource_stress'] = (df['cpu_usage_percent'] + df['memory_usage_percent']) / 2
    
    return df

def main():
    """Main function to generate and save synthetic dataset"""
    
    print("=" * 60)
    print("5G Testbed Synthetic Dataset Generator")
    print("=" * 60)
    print(f"\nGenerating {NUM_SAMPLES} samples...")
    
    # Generate dataset
    df = generate_network_data(NUM_SAMPLES, fault_probability=0.3)
    
    # Add derived features
    df = add_derived_features(df)
    
    # Display statistics
    print(f"\n✓ Dataset generated successfully!")
    print(f"\nDataset Shape: {df.shape}")
    print(f"\nFault Distribution:")
    print(df['fault_status'].value_counts())
    print(f"\nFault Percentage: {(df['fault_status'] == 'Faulty').sum() / len(df) * 100:.2f}%")
    
    # Save to CSV
    output_path = '../data/synthetic_5g_fault_dataset.csv'
    df.to_csv(output_path, index=False)
    print(f"\n✓ Dataset saved to: {output_path}")
    
    # Display sample records
    print("\n" + "=" * 60)
    print("Sample Records:")
    print("=" * 60)
    print(df.head(10))
    
    # Display basic statistics
    print("\n" + "=" * 60)
    print("Dataset Statistics:")
    print("=" * 60)
    print(df.describe())
    
    print("\n✓ Data generation complete!")

if __name__ == "__main__":
    main()
