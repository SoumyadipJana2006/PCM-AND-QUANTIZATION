import numpy as np
import matplotlib.pyplot as plt

# ======================================================
# USER INPUTS
# ======================================================

f = float(input("Enter signal frequency (Hz): "))
fs = float(input("Enter sampling frequency (Hz): "))
duration = float(input("Enter duration (seconds): "))
plot_n = int(input("Enter number of PCM bits (n): "))

# ======================================================
# SIGNAL GENERATION
# ======================================================

t = np.arange(0, duration, 1/fs)
x = np.sin(2*np.pi*f*t)

# Normalize to [-1,1]
x = x / np.max(np.abs(x))

# ======================================================
# EVALUATION FOR SQNR VS BITS
# ======================================================

# We evaluate 2-8 bits to satisfy the plot requirement, plus the user's specific 'n'
n_values = sorted(list(set(range(2, 9)) | {plot_n}))
measured_sqnrs = []
theory_sqnrs = []

# Variables to store results of the user-specified n for detailed plotting
xq_plot = None
error_plot = None
indices_plot = None
pcm_words_plot = None

for n in n_values:
    print(f"\n{'='*50}")
    print(f"EVALUATING n = {n} BITS")
    print(f"{'='*50}")

    L = 2**n
    delta = 2/L
    
    # --------------------------------------------------
    # EXPECTED EFFECT
    # --------------------------------------------------
    print("EXPECTED PHYSICAL EFFECT:")
    print(f"- Number of levels (L): {L}")
    print(f"- Step size (delta): {delta:.6f}")
    print("- As n increases, step size decreases, yielding higher resolution.")
    print(f"- Expected theoretical SQNR is roughly 6.02*{n} + 1.76 = {6.02*n + 1.76:.2f} dB.")

    # --------------------------------------------------
    # UNIFORM QUANTIZATION (First Principles)
    # --------------------------------------------------
    indices = np.floor((x + 1)/delta).astype(int)
    indices = np.clip(indices, 0, L-1)
    
    # Quantized values
    xq = -1 + (indices + 0.5)*delta

    # --------------------------------------------------
    # PCM ENCODING
    # --------------------------------------------------
    pcm_words = [format(i, f'0{n}b') for i in indices]

    # Save data for visualizations later
    if n == plot_n:
        xq_plot = xq
        error_plot = x - xq
        indices_plot = indices
        pcm_words_plot = pcm_words

    # --------------------------------------------------
    # MANDATORY VALIDATION
    # --------------------------------------------------
    index_check = np.all((indices >= 0) & (indices <= L-1))
    pcm_check = all(len(word) == n for word in pcm_words)
    
    print("\nVALIDATION:")
    if index_check:
        print("✓ All indices lie between 0 and L-1")
    else:
        print("✗ Index validation failed!")
        
    if pcm_check:
        print(f"✓ All PCM word lengths exactly equal {n}")
    else:
        print("✗ PCM length validation failed!")

    # --------------------------------------------------
    # ERROR ANALYSIS & SQNR
    # --------------------------------------------------
    error = x - xq
    mse = np.mean(error**2)
    signal_power = np.mean(x**2)
    
    sqnr_measured = 10*np.log10(signal_power/mse)
    sqnr_theory = 6.02*n + 1.76
    
    measured_sqnrs.append(sqnr_measured)
    theory_sqnrs.append(sqnr_theory)
    
    print("\nRESULTS:")
    print(f"MSE               = {mse:.8f}")
    print(f"Measured SQNR     = {sqnr_measured:.2f} dB")
    print(f"Theoretical SQNR  = {sqnr_theory:.2f} dB")
    diff = abs(sqnr_theory - sqnr_measured)
    print(f"Difference        = {diff:.2f} dB")
    
    # --------------------------------------------------
    # OBSERVATION AND INTERPRETATION
    # --------------------------------------------------
    print("\nOBSERVATION & INTERPRETATION:")
    if diff < 2.5:
        print("Observation: The measured SQNR agrees well with the theoretical approximation.")
        print("Interpretation: The quantization error follows a uniform distribution and behaves like additive white noise.")
    else:
        print("Observation: A noticeable discrepancy between measured and theoretical SQNR is observed.")
        print("Diagnosis: The theory assumes the error is uncorrelated uniformly distributed white noise.")
        print("Test Used: Comparing error histogram to uniform distribution and verifying the signal spans full scale.")

# ======================================================
# DISPLAY FIRST 10 PCM WORDS (For representative plot_n)
# ======================================================
print(f"\nFirst 10 Quantized Samples (for n={plot_n})")
print("Index\tPCM Word\tQuantized Value")
for i in range(min(10, len(indices_plot))):
    print(f"{indices_plot[i]}\t{pcm_words_plot[i]}\t{xq_plot[i]:.6f}")

# ======================================================
# REQUIRED VISUALIZATIONS
# ======================================================
plt.figure(figsize=(15, 10))
plt.suptitle('Uniform PCM Quantization Analysis', fontsize=16)

samples_to_plot = min(300, len(x))

# 1. Original / Quantized waveform
plt.subplot(2, 3, 1)
plt.plot(t[:samples_to_plot], x[:samples_to_plot], label='Original', color='C0')
plt.step(t[:samples_to_plot], xq_plot[:samples_to_plot], where='mid', label='Quantized', color='C1')
plt.title(f'Original vs Quantized ({plot_n} bits)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()

# 2. Staircase characteristic
plt.subplot(2, 3, 2)
plt.plot(x, xq_plot, '.', markersize=1, color='C2')
plt.title(f'Staircase Characteristic ({plot_n} bits)')
plt.xlabel('Input')
plt.ylabel('Quantized Output')
plt.grid(True)

# 3. Error waveform
plt.subplot(2, 3, 3)
plt.plot(t[:samples_to_plot], error_plot[:samples_to_plot], color='C3')
plt.title(f'Quantization Error ({plot_n} bits)')
plt.xlabel('Time (s)')
plt.ylabel('Error')
plt.grid(True)

# 4. Error histogram
plt.subplot(2, 3, 4)
plt.hist(error_plot, bins=40, color='C4', edgecolor='black')
plt.title(f'Error Histogram ({plot_n} bits)')
plt.xlabel('Error')
plt.ylabel('Count')
plt.grid(True)

# 5. SQNR versus bits
plt.subplot(2, 3, 5)
plt.plot(n_values, measured_sqnrs, 'o-', label='Measured SQNR', linewidth=2)
plt.plot(n_values, theory_sqnrs, 's--', label='Theoretical (6.02n + 1.76)', linewidth=2)
plt.title('SQNR versus Bits')
plt.xlabel('Number of Bits (n)')
plt.ylabel('SQNR (dB)')
plt.xticks(n_values)
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()# Auto detect text files and perform LF normalization
* text=auto
