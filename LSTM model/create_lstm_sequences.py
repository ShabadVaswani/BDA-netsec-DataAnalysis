import pandas as pd
import numpy as np
import os

# 1. Load the normalized data
print("Loading normalized data...")
data_path = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\LSTM model\health_net_features_2_normalize.csv'
df = pd.read_csv(data_path)

print(f"Original shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# 2. Drop non-numeric timestamp columns
timestamp_columns = ['datetime', 'date', 'time', 'hour', 'minute', 'day_of_week', 'day_numeric']
print(f"\nDropping timestamp columns: {timestamp_columns}")

# Keep only numeric feature columns
df_features = df.drop(columns=timestamp_columns)
print(f"Features shape after dropping timestamps: {df_features.shape}")
print(f"Feature columns: {list(df_features.columns)}")

# Convert to numpy array
data_array = df_features.values
print(f"\nData array shape: {data_array.shape}")

# Find the index of 'stress_level' column
target_column = 'stress_level'
target_column_index = df_features.columns.get_loc(target_column)
print(f"Target column '{target_column}' is at index: {target_column_index}")

# 3. Define function to create sequences
def create_sequences(data, target_column_index, window_size=60):
    """
    Create sliding window sequences for LSTM.
    
    Parameters:
    - data: numpy array of shape (samples, features)
    - target_column_index: index of the target column in the data
    - window_size: number of time steps to look back
    
    Returns:
    - X: 3D array of shape (num_sequences, window_size, num_features)
    - y: 1D array of shape (num_sequences,) containing target values
    """
    X = []
    y = []
    
    # Loop through the data, creating sequences
    for i in range(window_size, len(data)):
        # Get the past 'window_size' minutes of all features
        X.append(data[i - window_size:i, :])
        
        # Get the stress_level at the current time step (61st minute)
        y.append(data[i, target_column_index])
    
    return np.array(X), np.array(y)

# 4. Create sequences
print(f"\n{'='*80}")
print("Creating sequences with window_size=60...")
print(f"{'='*80}")

window_size = 60
X, y = create_sequences(data_array, target_column_index, window_size)

print(f"\nSequences created!")
print(f"X shape: {X.shape}  (samples, time_steps, features)")
print(f"y shape: {y.shape}  (samples,)")

# 5. Split into Train (80%) and Test (20%) - chronologically
print(f"\n{'='*80}")
print("Splitting data chronologically (80% train, 20% test)...")
print(f"{'='*80}")

split_index = int(len(X) * 0.8)

X_train = X[:split_index]
y_train = y[:split_index]
X_test = X[split_index:]
y_test = y[split_index:]

# 6. Print shapes
print(f"\nTrain set:")
print(f"  X_train shape: {X_train.shape}")
print(f"  y_train shape: {y_train.shape}")

print(f"\nTest set:")
print(f"  X_test shape: {X_test.shape}")
print(f"  y_test shape: {y_test.shape}")

# 7. Save arrays as .npy files
print(f"\n{'='*80}")
print("Saving arrays to .npy files...")
print(f"{'='*80}")

output_dir = r'c:\Users\shaba\Documents\Collage\BDA-netsec-DataAnalysis\LSTM model'

np.save(os.path.join(output_dir, 'X_train.npy'), X_train)
np.save(os.path.join(output_dir, 'y_train.npy'), y_train)
np.save(os.path.join(output_dir, 'X_test.npy'), X_test)
np.save(os.path.join(output_dir, 'y_test.npy'), y_test)

print(f"\n✓ Saved: X_train.npy")
print(f"✓ Saved: y_train.npy")
print(f"✓ Saved: X_test.npy")
print(f"✓ Saved: y_test.npy")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"Window size: {window_size} minutes")
print(f"Number of features: {X.shape[2]}")
print(f"Total sequences: {len(X):,}")
print(f"Training sequences: {len(X_train):,} ({len(X_train)/len(X)*100:.1f}%)")
print(f"Testing sequences: {len(X_test):,} ({len(X_test)/len(X)*100:.1f}%)")
print(f"\nAll files saved to: {output_dir}")
print("\n✓ Data preparation complete! Ready for LSTM training.")
