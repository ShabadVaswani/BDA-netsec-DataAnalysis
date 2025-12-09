"""
EXO-Hypermind: Hyperdimensional Transformer Autoencoder
A high-performance architecture combining SIREN activations, Transformer blocks,
and Latent ODE approximation for time-series reconstruction and anomaly detection.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
from pathlib import Path

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)


class SIRENLayer(layers.Layer):
    """
    SIREN (Sinusoidal Representation Networks) Dense Layer.
    Uses sine activation with He uniform initialization.
    """
    def __init__(self, units, **kwargs):
        super(SIRENLayer, self).__init__(**kwargs)
        self.units = units
        
    def build(self, input_shape):
        self.dense = layers.Dense(
            self.units,
            kernel_initializer='he_uniform',
            use_bias=True
        )
        super(SIRENLayer, self).build(input_shape)
    
    def call(self, inputs):
        x = self.dense(inputs)
        return tf.math.sin(x)
    
    def get_config(self):
        config = super(SIRENLayer, self).get_config()
        config.update({"units": self.units})
        return config


class PositionalEncoding(layers.Layer):
    """
    Positional Encoding for Transformer to capture temporal order.
    """
    def __init__(self, max_len=60, d_model=128, **kwargs):
        super(PositionalEncoding, self).__init__(**kwargs)
        self.max_len = max_len
        self.d_model = d_model
        
    def build(self, input_shape):
        # Create positional encoding matrix
        position = np.arange(self.max_len)[:, np.newaxis]
        div_term = np.exp(np.arange(0, self.d_model, 2) * -(np.log(10000.0) / self.d_model))
        
        pe = np.zeros((self.max_len, self.d_model))
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)
        
        self.pos_encoding = tf.constant(pe, dtype=tf.float32)
        super(PositionalEncoding, self).build(input_shape)
    
    def call(self, inputs):
        seq_len = tf.shape(inputs)[1]
        return inputs + self.pos_encoding[:seq_len, :]
    
    def get_config(self):
        config = super(PositionalEncoding, self).get_config()
        config.update({"max_len": self.max_len, "d_model": self.d_model})
        return config


def build_exo_hypermind(input_shape, num_features):
    """
    Build the EXO-Hypermind architecture.
    
    Architecture:
    1. Hyperdimensional Projection (SIREN)
    2. Temporal Dynamics (Transformer)
    3. Latent ODE Approximation (Residual Block)
    4. Reconstruction
    
    Args:
        input_shape: Tuple (timesteps, features)
        num_features: Number of features in the input
        
    Returns:
        Keras Model
    """
    # INPUT
    inputs = layers.Input(shape=input_shape, name='input')
    
    # ============================================================
    # STAGE 1: HYPERDIMENSIONAL PROJECTION (SIREN)
    # ============================================================
    # Project to 64 dimensions
    x = SIRENLayer(64, name='siren_projection_64')(inputs)
    
    # Project to 128 dimensions
    x = SIRENLayer(128, name='siren_projection_128')(x)
    
    # ============================================================
    # STAGE 2: TEMPORAL DYNAMICS (Transformer)
    # ============================================================
    # Positional Encoding
    x = PositionalEncoding(max_len=input_shape[0], d_model=128, name='positional_encoding')(x)
    
    # Multi-Head Attention
    attention_output = layers.MultiHeadAttention(
        num_heads=4,
        key_dim=32,
        name='multi_head_attention'
    )(x, x)
    
    # Add & Norm 1
    x = layers.Add(name='add_attention')([x, attention_output])
    x = layers.LayerNormalization(epsilon=1e-6, name='norm_attention')(x)
    
    # Feed Forward Network
    ffn = layers.Dense(128, activation='relu', name='ffn_dense_1')(x)
    ffn = layers.Dense(128, name='ffn_dense_2')(ffn)
    
    # Add & Norm 2
    x = layers.Add(name='add_ffn')([x, ffn])
    x = layers.LayerNormalization(epsilon=1e-6, name='norm_ffn')(x)
    
    # ============================================================
    # STAGE 3: LATENT ODE APPROXIMATION (Residual Block)
    # ============================================================
    # Dense with swish activation (simulates ODE dynamics)
    ode_step = layers.Dense(128, activation='swish', name='ode_dense')(x)
    
    # Skip connection (Euler integration step)
    x = layers.Add(name='ode_residual')([x, ode_step])
    
    # ============================================================
    # STAGE 4: RECONSTRUCTION
    # ============================================================
    # Apply Dense layer to each timestep independently to reconstruct features
    outputs = layers.TimeDistributed(
        layers.Dense(num_features, activation='linear'),
        name='reconstruction'
    )(x)
    
    # Create model
    model = models.Model(inputs=inputs, outputs=outputs, name='EXO_Hypermind')
    
    return model


def calculate_exo_psi_index(y_true, y_pred):
    """
    Calculate the EXO-Psi Stability Index.
    
    The index converts reconstruction error to a 0-100 score where:
    - 100 = Perfect reconstruction
    - Lower scores indicate higher anomaly/instability
    
    Args:
        y_true: Ground truth data
        y_pred: Predicted/reconstructed data
        
    Returns:
        psi_scores: Array of EXO-Psi scores (0-100) for each sample
        reconstruction_errors: MSE per sample
    """
    # Calculate MSE per sample
    reconstruction_errors = np.mean((y_true - y_pred) ** 2, axis=(1, 2))
    
    # Auto-calculate scaling factor
    # We want average error to map to ~20 points deduction
    # So average score should be around 80
    mean_error = np.mean(reconstruction_errors)
    scaling_factor = 20 / mean_error if mean_error > 0 else 1.0
    
    # Convert to 0-100 score
    psi_scores = np.maximum(0, 100 - (reconstruction_errors * scaling_factor))
    
    print(f"\n=== EXO-Psi Stability Index Statistics ===")
    print(f"Mean Reconstruction Error: {mean_error:.6f}")
    print(f"Scaling Factor: {scaling_factor:.2f}")
    print(f"Mean Psi Score: {np.mean(psi_scores):.2f}")
    print(f"Std Psi Score: {np.std(psi_scores):.2f}")
    print(f"Min Psi Score: {np.min(psi_scores):.2f}")
    print(f"Max Psi Score: {np.max(psi_scores):.2f}")
    
    return psi_scores, reconstruction_errors


def plot_exo_psi_index(psi_scores, save_path='exo_psi_visualization.png'):
    """
    Visualize the EXO-Psi Stability Index over time.
    
    Args:
        psi_scores: Array of Psi scores
        save_path: Path to save the plot
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Psi Index over time
    axes[0].plot(psi_scores, linewidth=0.5, alpha=0.7, color='#2E86AB')
    axes[0].axhline(y=80, color='green', linestyle='--', label='Stable Threshold (80)', alpha=0.7)
    axes[0].axhline(y=50, color='orange', linestyle='--', label='Warning Threshold (50)', alpha=0.7)
    axes[0].axhline(y=20, color='red', linestyle='--', label='Critical Threshold (20)', alpha=0.7)
    axes[0].set_xlabel('Sample Index', fontsize=12)
    axes[0].set_ylabel('EXO-Psi Stability Index', fontsize=12)
    axes[0].set_title('EXO-Psi Stability Index Over Time', fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim([0, 105])
    
    # Plot 2: Distribution histogram
    axes[1].hist(psi_scores, bins=50, color='#A23B72', alpha=0.7, edgecolor='black')
    axes[1].axvline(x=np.mean(psi_scores), color='blue', linestyle='--', 
                    label=f'Mean: {np.mean(psi_scores):.2f}', linewidth=2)
    axes[1].set_xlabel('EXO-Psi Stability Index', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Distribution of EXO-Psi Stability Index', fontsize=14, fontweight='bold')
    axes[1].legend(loc='upper left')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved to: {save_path}")
    plt.show()


def main():
    """
    Main execution function.
    """
    print("=" * 60)
    print("EXO-Hypermind: Hyperdimensional Transformer Autoencoder")
    print("=" * 60)
    
    # ============================================================
    # 1. LOAD DATA
    # ============================================================
    print("\n[1/6] Loading data...")
    X_train = np.load('X_train.npy')
    X_test = np.load('X_test.npy')
    
    print(f"✓ X_train shape: {X_train.shape}")
    print(f"✓ X_test shape: {X_test.shape}")
    print(f"✓ Data range: [{X_train.min():.4f}, {X_train.max():.4f}]")
    
    # Extract dimensions
    timesteps = X_train.shape[1]
    num_features = X_train.shape[2]
    
    # ============================================================
    # 2. BUILD MODEL
    # ============================================================
    print("\n[2/6] Building EXO-Hypermind architecture...")
    model = build_exo_hypermind(input_shape=(timesteps, num_features), num_features=num_features)
    
    # Print model summary
    model.summary()
    
    # ============================================================
    # 3. COMPILE MODEL
    # ============================================================
    print("\n[3/6] Compiling model with AdamW optimizer...")
    
    # Use AdamW (Adam with weight decay) for better regularization
    optimizer = tf.keras.optimizers.AdamW(
        learning_rate=0.001,
        weight_decay=0.0001
    )
    
    model.compile(
        optimizer=optimizer,
        loss='mse',
        metrics=['mae']
    )
    
    # ============================================================
    # 4. TRAIN MODEL
    # ============================================================
    print("\n[4/6] Training model...")
    
    # Callbacks
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-6,
        verbose=1
    )
    
    # Train the model
    history = model.fit(
        X_train, X_train,  # Autoencoder: input = output
        validation_data=(X_test, X_test),
        epochs=40,
        batch_size=32,
        callbacks=[early_stopping, reduce_lr],
        verbose=1
    )
    
    # ============================================================
    # 5. CALCULATE EXO-PSI STABILITY INDEX
    # ============================================================
    print("\n[5/6] Calculating EXO-Psi Stability Index...")
    
    # Predict on test set
    X_test_pred = model.predict(X_test, verbose=0)
    
    # Calculate Psi scores
    psi_scores, reconstruction_errors = calculate_exo_psi_index(X_test, X_test_pred)
    
    # Save scores
    np.save('exo_psi_scores.npy', psi_scores)
    print(f"✓ Psi scores saved to: exo_psi_scores.npy")
    
    # ============================================================
    # 6. VISUALIZE RESULTS
    # ============================================================
    print("\n[6/6] Generating visualizations...")
    
    # Plot Psi Index
    plot_exo_psi_index(psi_scores)
    
    # Plot training history
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Loss plot
    axes[0].plot(history.history['loss'], label='Training Loss', linewidth=2)
    axes[0].plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss (MSE)', fontsize=12)
    axes[0].set_title('Training History - Loss', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # MAE plot
    axes[1].plot(history.history['mae'], label='Training MAE', linewidth=2)
    axes[1].plot(history.history['val_mae'], label='Validation MAE', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('MAE', fontsize=12)
    axes[1].set_title('Training History - MAE', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
    print(f"✓ Training history saved to: training_history.png")
    plt.show()
    
    # ============================================================
    # SAVE MODEL
    # ============================================================
    print("\n[FINAL] Saving model...")
    model.save('exo_hypermind_model.keras')
    print(f"✓ Model saved to: exo_hypermind_model.keras")
    
    print("\n" + "=" * 60)
    print("EXO-Hypermind Training Complete!")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Model: exo_hypermind_model.keras")
    print(f"  - Psi Scores: exo_psi_scores.npy")
    print(f"  - Visualization: exo_psi_visualization.png")
    print(f"  - Training History: training_history.png")
    print("\n")


if __name__ == "__main__":
    main()
