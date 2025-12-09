"""
Bio-Exclusive Variational Autoencoder (VAE)
============================================
This script builds a VAE that focuses exclusively on physiological/biological features,
ignoring environmental and digital features for anomaly detection.

Features used:
- heart_rate
- stress_level
- body_battery
- sleep_duration_of_day
- stress_rolling_mean_30
- stress_volatility_30
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping
import seaborn as sns

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

print("=" * 80)
print("BIO-EXCLUSIVE VAE - ANOMALY DETECTION")
print("=" * 80)

# ============================================================================
# STEP 1: Feature Slicing - Extract Biological Features Only
# ============================================================================
print("\n[STEP 1] Loading data and extracting biological features...")

# Load column names
features_df = pd.read_csv('health_net_features_2_normalize.csv', nrows=0)
column_names = features_df.columns.tolist()
print(f"Total features in dataset: {len(column_names)}")

# Define biological features we want to keep
bio_features = [
    'heart_rate',
    'stress_level', 
    'body_battery',
    'sleep_duration_of_day',
    'stress_rolling_mean_30',
    'stress_volatility_30'
]

# Find indices of biological features
bio_indices = [column_names.index(feat) for feat in bio_features]
print(f"\nBiological features selected: {bio_features}")
print(f"Feature indices: {bio_indices}")

# Load training and test data
X_train = np.load('X_train.npy')
X_test = np.load('X_test.npy')

print(f"\nOriginal shapes:")
print(f"  X_train: {X_train.shape}")
print(f"  X_test: {X_test.shape}")

# Slice to keep only biological features
X_train_bio = X_train[:, :, bio_indices]
X_test_bio = X_test[:, :, bio_indices]

print(f"\nBio-sliced shapes:")
print(f"  X_train_bio: {X_train_bio.shape}")
print(f"  X_test_bio: {X_test_bio.shape}")

# ============================================================================
# STEP 2: Define VAE Architecture
# ============================================================================
print("\n[STEP 2] Building Bio-Exclusive VAE architecture...")

# Hyperparameters
TIMESTEPS = 60
NUM_BIO_FEATURES = 6
LATENT_DIM = 2
HIDDEN_DIM = 16
LEARNING_RATE = 0.001
EPOCHS = 30
BATCH_SIZE = 32

# Custom Sampling Layer (Reparameterization Trick)
class Sampling(layers.Layer):
    """Uses (z_mean, z_log_var) to sample z, the vector encoding a digit."""
    
    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon


# Encoder
def build_encoder(timesteps, num_features, latent_dim, hidden_dim):
    """Build the encoder network."""
    encoder_inputs = keras.Input(shape=(timesteps, num_features), name='encoder_input')
    
    # Flatten the input
    x = layers.Flatten()(encoder_inputs)
    
    # Hidden layer
    x = layers.Dense(hidden_dim, activation='relu', name='encoder_hidden')(x)
    
    # Latent space parameters
    z_mean = layers.Dense(latent_dim, name='z_mean')(x)
    z_log_var = layers.Dense(latent_dim, name='z_log_var')(x)
    
    # Sample from latent space
    z = Sampling()([z_mean, z_log_var])
    
    encoder = Model(encoder_inputs, [z_mean, z_log_var, z], name='encoder')
    return encoder


# Decoder
def build_decoder(timesteps, num_features, latent_dim, hidden_dim):
    """Build the decoder network."""
    latent_inputs = keras.Input(shape=(latent_dim,), name='decoder_input')
    
    # Hidden layer
    x = layers.Dense(hidden_dim, activation='relu', name='decoder_hidden')(latent_inputs)
    
    # Output layer
    x = layers.Dense(timesteps * num_features, activation='linear', name='decoder_output')(x)
    
    # Reshape to original dimensions
    decoder_outputs = layers.Reshape((timesteps, num_features))(x)
    
    decoder = Model(latent_inputs, decoder_outputs, name='decoder')
    return decoder


# Custom VAE Model
class BioVAE(Model):
    """Bio-Exclusive Variational Autoencoder."""
    
    def __init__(self, encoder, decoder, **kwargs):
        super(BioVAE, self).__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.total_loss_tracker = keras.metrics.Mean(name="total_loss")
        self.reconstruction_loss_tracker = keras.metrics.Mean(name="reconstruction_loss")
        self.kl_loss_tracker = keras.metrics.Mean(name="kl_loss")
    
    @property
    def metrics(self):
        return [
            self.total_loss_tracker,
            self.reconstruction_loss_tracker,
            self.kl_loss_tracker,
        ]
    
    def train_step(self, data):
        with tf.GradientTape() as tape:
            # Forward pass
            z_mean, z_log_var, z = self.encoder(data)
            reconstruction = self.decoder(z)
            
            # Reconstruction loss (MSE)
            reconstruction_loss = tf.reduce_mean(
                tf.reduce_sum(
                    keras.losses.mean_squared_error(data, reconstruction),
                    axis=1
                )
            )
            
            # KL divergence loss
            kl_loss = -0.5 * tf.reduce_mean(
                tf.reduce_sum(
                    1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var),
                    axis=1
                )
            )
            
            # Total loss
            total_loss = reconstruction_loss + kl_loss
        
        # Backpropagation
        grads = tape.gradient(total_loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))
        
        # Update metrics
        self.total_loss_tracker.update_state(total_loss)
        self.reconstruction_loss_tracker.update_state(reconstruction_loss)
        self.kl_loss_tracker.update_state(kl_loss)
        
        return {
            "total_loss": self.total_loss_tracker.result(),
            "reconstruction_loss": self.reconstruction_loss_tracker.result(),
            "kl_loss": self.kl_loss_tracker.result(),
        }
    
    def call(self, inputs):
        """Forward pass through the VAE."""
        z_mean, z_log_var, z = self.encoder(inputs)
        reconstruction = self.decoder(z)
        return reconstruction


# Build the model
print("\nBuilding encoder...")
encoder = build_encoder(TIMESTEPS, NUM_BIO_FEATURES, LATENT_DIM, HIDDEN_DIM)
encoder.summary()

print("\nBuilding decoder...")
decoder = build_decoder(TIMESTEPS, NUM_BIO_FEATURES, LATENT_DIM, HIDDEN_DIM)
decoder.summary()

print("\nBuilding Bio-Exclusive VAE...")
vae = BioVAE(encoder, decoder)

# ============================================================================
# STEP 3: Train the VAE
# ============================================================================
print("\n[STEP 3] Training the Bio-Exclusive VAE...")

# Compile the model
vae.compile(optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE))

# Early stopping callback
early_stopping = EarlyStopping(
    monitor='total_loss',
    patience=5,
    restore_best_weights=True,
    verbose=1
)

# Train the model
history = vae.fit(
    X_train_bio,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[early_stopping],
    verbose=1
)

print("\n✓ Training complete!")

# Plot training history
plt.figure(figsize=(15, 4))

plt.subplot(1, 3, 1)
plt.plot(history.history['total_loss'])
plt.title('Total Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.grid(True, alpha=0.3)

plt.subplot(1, 3, 2)
plt.plot(history.history['reconstruction_loss'])
plt.title('Reconstruction Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.grid(True, alpha=0.3)

plt.subplot(1, 3, 3)
plt.plot(history.history['kl_loss'])
plt.title('KL Divergence Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('bio_vae_training_history.png', dpi=150, bbox_inches='tight')
print("✓ Training history plot saved as 'bio_vae_training_history.png'")
plt.show()

# ============================================================================
# STEP 4: Calculate Bio-Stability Scores
# ============================================================================
print("\n[STEP 4] Calculating Bio-Stability Scores...")

# Get reconstructions for test set
reconstructions = vae.predict(X_test_bio, verbose=0)

# Calculate reconstruction error (MSE) for each sample
reconstruction_errors = np.mean(np.square(X_test_bio - reconstructions), axis=(1, 2))

print(f"\nReconstruction Error Statistics:")
print(f"  Mean: {reconstruction_errors.mean():.6f}")
print(f"  Std:  {reconstruction_errors.std():.6f}")
print(f"  Min:  {reconstruction_errors.min():.6f}")
print(f"  Max:  {reconstruction_errors.max():.6f}")

# Auto-calculate scaling factor
# Target: Average score = 80 (meaning average error deducts 20 points)
TARGET_AVG_SCORE = 80.0
TARGET_AVG_DEDUCTION = 100.0 - TARGET_AVG_SCORE
mean_error = reconstruction_errors.mean()
scaling_factor = TARGET_AVG_DEDUCTION / mean_error

print(f"\nScaling Factor Calculation:")
print(f"  Target Average Score: {TARGET_AVG_SCORE}")
print(f"  Mean Reconstruction Error: {mean_error:.6f}")
print(f"  Calculated Scaling Factor: {scaling_factor:.2f}")

# Calculate Bio-Stability Scores
# Score = max(0, 100 - (Error * Scaling_Factor))
bio_stability_scores = np.maximum(0, 100 - (reconstruction_errors * scaling_factor))

print(f"\nBio-Stability Score Statistics:")
print(f"  Mean: {bio_stability_scores.mean():.2f}")
print(f"  Std:  {bio_stability_scores.std():.2f}")
print(f"  Min:  {bio_stability_scores.min():.2f}")
print(f"  Max:  {bio_stability_scores.max():.2f}")

# ============================================================================
# STEP 5: Save Results & Visualize
# ============================================================================
print("\n[STEP 5] Saving results and creating visualizations...")

# Save the scores
np.save('bio_stability_scores.npy', bio_stability_scores)
print("✓ Saved 'bio_stability_scores.npy'")

# Save the sliced test data
np.save('X_test_bio.npy', X_test_bio)
print("✓ Saved 'X_test_bio.npy'")

# Save the model
vae.save_weights('bio_vae_weights.h5')
print("✓ Saved model weights as 'bio_vae_weights.h5'")

# Visualization 1: Bio-Stability Score Over Time
plt.figure(figsize=(16, 6))

plt.subplot(2, 1, 1)
plt.plot(bio_stability_scores, linewidth=0.8, alpha=0.7, color='#2E86AB')
plt.axhline(y=bio_stability_scores.mean(), color='red', linestyle='--', 
            label=f'Mean: {bio_stability_scores.mean():.2f}', linewidth=2)
plt.fill_between(range(len(bio_stability_scores)), 0, bio_stability_scores, 
                 alpha=0.2, color='#2E86AB')
plt.title('Bio-Stability Score Over Time', fontsize=14, fontweight='bold')
plt.xlabel('Sample Index (Time)', fontsize=11)
plt.ylabel('Bio-Stability Score', fontsize=11)
plt.ylim(0, 105)
plt.grid(True, alpha=0.3)
plt.legend()

# Visualization 2: Score Distribution
plt.subplot(2, 1, 2)
plt.hist(bio_stability_scores, bins=50, color='#A23B72', alpha=0.7, edgecolor='black')
plt.axvline(x=bio_stability_scores.mean(), color='red', linestyle='--', 
            label=f'Mean: {bio_stability_scores.mean():.2f}', linewidth=2)
plt.title('Bio-Stability Score Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Bio-Stability Score', fontsize=11)
plt.ylabel('Frequency', fontsize=11)
plt.grid(True, alpha=0.3, axis='y')
plt.legend()

plt.tight_layout()
plt.savefig('bio_stability_scores_visualization.png', dpi=150, bbox_inches='tight')
print("✓ Saved visualization as 'bio_stability_scores_visualization.png'")
plt.show()

# Additional Visualization: Reconstruction Error vs Score
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Reconstruction Error Over Time
axes[0].plot(reconstruction_errors, linewidth=0.8, alpha=0.7, color='#F18F01')
axes[0].axhline(y=reconstruction_errors.mean(), color='red', linestyle='--', 
                label=f'Mean: {reconstruction_errors.mean():.4f}', linewidth=2)
axes[0].set_title('Reconstruction Error Over Time', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Sample Index (Time)', fontsize=11)
axes[0].set_ylabel('MSE Reconstruction Error', fontsize=11)
axes[0].grid(True, alpha=0.3)
axes[0].legend()

# Scatter: Error vs Score
axes[1].scatter(reconstruction_errors, bio_stability_scores, alpha=0.5, s=10, color='#6A4C93')
axes[1].set_title('Reconstruction Error vs Bio-Stability Score', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Reconstruction Error (MSE)', fontsize=11)
axes[1].set_ylabel('Bio-Stability Score', fontsize=11)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('bio_reconstruction_analysis.png', dpi=150, bbox_inches='tight')
print("✓ Saved analysis plot as 'bio_reconstruction_analysis.png'")
plt.show()

# Summary Statistics
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✓ Biological features extracted: {NUM_BIO_FEATURES}")
print(f"✓ Training samples: {X_train_bio.shape[0]}")
print(f"✓ Test samples: {X_test_bio.shape[0]}")
print(f"✓ Latent dimension: {LATENT_DIM}")
print(f"✓ Average Bio-Stability Score: {bio_stability_scores.mean():.2f}")
print(f"✓ Scaling Factor: {scaling_factor:.2f}")
print(f"✓ Model trained for {len(history.history['total_loss'])} epochs")
print("=" * 80)
print("\n✓ All files saved successfully!")
print("  - bio_stability_scores.npy")
print("  - X_test_bio.npy")
print("  - bio_vae_weights.h5")
print("  - bio_vae_training_history.png")
print("  - bio_stability_scores_visualization.png")
print("  - bio_reconstruction_analysis.png")
print("\n" + "=" * 80)
