"""
Dispersion Analysis: Extract ω(k) from Field Evolution

This module analyzes coherence field evolution to extract dispersion relations:
    ω²(k) = m² + c²k² + αk⁴

Where:
    - ω: Angular frequency
    - k: Wavenumber
    - m: Mass gap (from potential term)
    - c: Phase velocity (speed of propagation)
    - α: Skyrme coefficient (quartic dispersion)

Methods:
    1. FFT-based: Transform field data to (k,ω) space
    2. Peak detection: Find dominant frequency for each k
    3. Curve fitting: Fit dispersion relation to extracted points
    4. Statistical analysis: Confidence intervals and goodness-of-fit

Author: FIRM-Core Development Team
Date: 2025-10-08
Version: 1.0.0
"""

import numpy as np
from typing import Tuple, Dict, List, Optional, Callable
from dataclasses import dataclass
from scipy import fft
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, periodogram
from scipy.stats import linregress
import warnings

# Import field equations for type hints
try:
    from field_equations import CoherenceField, FieldParameters, GridParameters
    FIELD_EQUATIONS_AVAILABLE = True
except ImportError:
    FIELD_EQUATIONS_AVAILABLE = False


@dataclass
class DispersionParameters:
    """
    Parameters extracted from dispersion relation fit.
    
    ω²(k) = m² + c²k² + αk⁴
    
    Attributes:
        mass: Mass gap m (ω(k=0))
        c: Phase velocity (linear term coefficient)
        alpha: Skyrme coefficient (quartic term coefficient)
        mass_err: Standard error on mass
        c_err: Standard error on c
        alpha_err: Standard error on alpha
        r_squared: R² goodness-of-fit
    """
    mass: float
    c: float
    alpha: float
    mass_err: float = 0.0
    c_err: float = 0.0
    alpha_err: float = 0.0
    r_squared: float = 0.0
    
    def __str__(self) -> str:
        """Pretty print dispersion parameters."""
        return (
            f"Dispersion Relation: ω²(k) = m² + c²k² + αk⁴\n"
            f"  Mass gap (m):      {self.mass:.6f} ± {self.mass_err:.6f}\n"
            f"  Phase velocity (c): {self.c:.6f} ± {self.c_err:.6f}\n"
            f"  Skyrme coeff (α):   {self.alpha:.6f} ± {self.alpha_err:.6f}\n"
            f"  R²:                 {self.r_squared:.6f}"
        )


@dataclass
class DispersionData:
    """
    Extracted dispersion relation data points.
    
    Attributes:
        k: Wavenumber array
        omega: Angular frequency array
        omega_squared: ω² array
        amplitude: Amplitude of each (k,ω) mode
        k_bins: Number of k bins used
        omega_bins: Number of ω bins used
    """
    k: np.ndarray
    omega: np.ndarray
    omega_squared: np.ndarray
    amplitude: np.ndarray
    k_bins: int
    omega_bins: int
    
    def filter_by_amplitude(self, threshold: float = 0.1) -> 'DispersionData':
        """
        Filter data points by amplitude threshold.
        
        Args:
            threshold: Minimum amplitude (relative to max)
            
        Returns:
            Filtered DispersionData
        """
        max_amp = np.max(self.amplitude)
        mask = self.amplitude >= threshold * max_amp
        
        return DispersionData(
            k=self.k[mask],
            omega=self.omega[mask],
            omega_squared=self.omega_squared[mask],
            amplitude=self.amplitude[mask],
            k_bins=self.k_bins,
            omega_bins=self.omega_bins
        )


class DispersionAnalyzer:
    """
    Analyzes field evolution data to extract dispersion relations.
    
    Main workflow:
        1. Load time-series field data
        2. Compute 2D FFT: (x,t) → (k,ω)
        3. Extract peak frequencies for each k
        4. Fit dispersion relation ω²(k)
        5. Compute statistical measures
    """
    
    def __init__(self, field_data: np.ndarray, times: np.ndarray, grid_params):
        """
        Initialize dispersion analyzer.
        
        Args:
            field_data: Field component time series, shape (Nt, Nx) or (Nt, Nx, Ny)
            times: Time array (Nt,)
            grid_params: GridParameters object with spatial grid info
        """
        self.field_data = field_data
        self.times = times
        self.grid = grid_params
        
        # Validate inputs
        if len(times) != field_data.shape[0]:
            raise ValueError("times length must match field_data first dimension")
        
        if grid_params.is_1d and len(field_data.shape) != 2:
            raise ValueError("For 1D, field_data must have shape (Nt, Nx)")
        
        if not grid_params.is_1d and len(field_data.shape) != 3:
            raise ValueError("For 2D, field_data must have shape (Nt, Nx, Ny)")
        
        # Computed quantities
        self._fft_result = None
        self._k_values = None
        self._omega_values = None
    
    def compute_fft(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute 2D FFT: (x,t) → (k,ω).
        
        For 1D field: FFT over (t, x)
        For 2D field: FFT over (t, x) along each y (or average)
        
        Returns:
            Tuple of (k_values, omega_values, fft_magnitude)
        """
        if self.grid.is_1d:
            # 1D case: shape (Nt, Nx)
            # FFT over both dimensions
            fft_2d = fft.fft2(self.field_data)
            fft_2d_shifted = fft.fftshift(fft_2d)
            
            # Wavenumber array
            Nx = self.field_data.shape[1]
            k_vals = fft.fftshift(fft.fftfreq(Nx, d=self.grid.dx)) * 2 * np.pi
            
            # Frequency array
            Nt = len(self.times)
            dt = self.times[1] - self.times[0]
            omega_vals = fft.fftshift(fft.fftfreq(Nt, d=dt)) * 2 * np.pi
            
            fft_magnitude = np.abs(fft_2d_shifted)
            
        else:
            # 2D case: Average over y or take slice
            # For simplicity, average over y
            field_1d = np.mean(self.field_data, axis=2)  # (Nt, Nx)
            
            fft_2d = fft.fft2(field_1d)
            fft_2d_shifted = fft.fftshift(fft_2d)
            
            Nx = field_1d.shape[1]
            k_vals = fft.fftshift(fft.fftfreq(Nx, d=self.grid.dx)) * 2 * np.pi
            
            Nt = len(self.times)
            dt = self.times[1] - self.times[0]
            omega_vals = fft.fftshift(fft.fftfreq(Nt, d=dt)) * 2 * np.pi
            
            fft_magnitude = np.abs(fft_2d_shifted)
        
        # Cache results
        self._k_values = k_vals
        self._omega_values = omega_vals
        self._fft_result = fft_magnitude
        
        return k_vals, omega_vals, fft_magnitude
    
    def extract_dispersion_peaks(
        self,
        k_range: Optional[Tuple[float, float]] = None,
        omega_range: Optional[Tuple[float, float]] = None,
        min_amplitude: float = 0.1
    ) -> DispersionData:
        """
        Extract dispersion relation by finding peak ω for each k.
        
        Args:
            k_range: (k_min, k_max) to analyze (None = all positive k)
            omega_range: (ω_min, ω_max) to analyze (None = all positive ω)
            min_amplitude: Minimum peak amplitude (relative to max)
            
        Returns:
            DispersionData with extracted (k,ω) points
        """
        # Ensure FFT is computed
        if self._fft_result is None:
            self.compute_fft()
        
        k_vals = self._k_values
        omega_vals = self._omega_values
        fft_mag = self._fft_result
        
        # Restrict to positive frequencies (physical)
        omega_positive_mask = omega_vals >= 0
        omega_vals_pos = omega_vals[omega_positive_mask]
        fft_mag_pos = fft_mag[omega_positive_mask, :]
        
        # Restrict to k range
        if k_range is not None:
            k_min, k_max = k_range
            k_mask = (k_vals >= k_min) & (k_vals <= k_max)
        else:
            # Use positive k
            k_mask = k_vals >= 0
        
        k_vals_selected = k_vals[k_mask]
        fft_mag_selected = fft_mag_pos[:, k_mask]
        
        # For each k, find peak ω
        k_list = []
        omega_list = []
        amplitude_list = []
        
        for i_k, k in enumerate(k_vals_selected):
            # Spectrum at this k
            spectrum = fft_mag_selected[:, i_k]
            
            # Apply omega range filter
            if omega_range is not None:
                omega_min, omega_max = omega_range
                omega_mask = (omega_vals_pos >= omega_min) & (omega_vals_pos <= omega_max)
                spectrum_filtered = spectrum[omega_mask]
                omega_vals_filtered = omega_vals_pos[omega_mask]
            else:
                spectrum_filtered = spectrum
                omega_vals_filtered = omega_vals_pos
            
            # Find peaks
            max_spectrum = np.max(spectrum_filtered)
            
            # If spectrum is non-zero, look for peaks
            if max_spectrum > 0:
                threshold = min_amplitude * max_spectrum
                peaks, properties = find_peaks(spectrum_filtered, height=threshold)
                
                if len(peaks) > 0:
                    # Take highest peak
                    i_peak = peaks[np.argmax(properties['peak_heights'])]
                    omega_peak = omega_vals_filtered[i_peak]
                    amplitude_peak = spectrum_filtered[i_peak]
                    
                    k_list.append(k)
                    omega_list.append(omega_peak)
                    amplitude_list.append(amplitude_peak)
                else:
                    # No peaks found, just take maximum
                    i_max = np.argmax(spectrum_filtered)
                    omega_peak = omega_vals_filtered[i_max]
                    amplitude_peak = spectrum_filtered[i_max]
                    
                    # Only add if amplitude is significant
                    if amplitude_peak > threshold:
                        k_list.append(k)
                        omega_list.append(omega_peak)
                        amplitude_list.append(amplitude_peak)
        
        # Convert to arrays
        k_array = np.array(k_list)
        omega_array = np.array(omega_list)
        omega_squared_array = omega_array**2
        amplitude_array = np.array(amplitude_list)
        
        return DispersionData(
            k=k_array,
            omega=omega_array,
            omega_squared=omega_squared_array,
            amplitude=amplitude_array,
            k_bins=len(k_vals_selected),
            omega_bins=len(omega_vals_pos)
        )
    
    def fit_dispersion_relation(
        self,
        data: DispersionData,
        fit_order: str = 'quartic'
    ) -> DispersionParameters:
        """
        Fit dispersion relation to extracted data.
        
        ω²(k) = m² + c²k² + αk⁴  (quartic)
        ω²(k) = m² + c²k²         (quadratic)
        ω²(k) = m² + αk⁴          (mass + quartic)
        
        Args:
            data: DispersionData to fit
            fit_order: 'quartic', 'quadratic', or 'mass_quartic'
            
        Returns:
            DispersionParameters with fitted values and errors
        """
        k = data.k
        omega_squared = data.omega_squared
        
        # Define fitting functions
        def quartic_model(k, m_sq, c_sq, alpha):
            return m_sq + c_sq * k**2 + alpha * k**4
        
        def quadratic_model(k, m_sq, c_sq):
            return m_sq + c_sq * k**2
        
        def mass_quartic_model(k, m_sq, alpha):
            return m_sq + alpha * k**4
        
        # Fit based on order
        try:
            if fit_order == 'quartic':
                # Full model
                popt, pcov = curve_fit(quartic_model, k, omega_squared, 
                                      p0=[1.0, 1.0, 0.1],
                                      bounds=([0, 0, 0], [np.inf, np.inf, np.inf]))
                m_sq, c_sq, alpha = popt
                m = np.sqrt(max(m_sq, 0))
                c = np.sqrt(max(c_sq, 0))
                
                # Errors
                perr = np.sqrt(np.diag(pcov))
                m_err = perr[0] / (2 * m) if m > 0 else 0
                c_err = perr[1] / (2 * c) if c > 0 else 0
                alpha_err = perr[2]
                
            elif fit_order == 'quadratic':
                # No quartic term
                popt, pcov = curve_fit(quadratic_model, k, omega_squared,
                                      p0=[1.0, 1.0],
                                      bounds=([0, 0], [np.inf, np.inf]))
                m_sq, c_sq = popt
                m = np.sqrt(max(m_sq, 0))
                c = np.sqrt(max(c_sq, 0))
                alpha = 0.0
                
                perr = np.sqrt(np.diag(pcov))
                m_err = perr[0] / (2 * m) if m > 0 else 0
                c_err = perr[1] / (2 * c) if c > 0 else 0
                alpha_err = 0.0
                
            elif fit_order == 'mass_quartic':
                # No quadratic term
                popt, pcov = curve_fit(mass_quartic_model, k, omega_squared,
                                      p0=[1.0, 0.1],
                                      bounds=([0, 0], [np.inf, np.inf]))
                m_sq, alpha = popt
                m = np.sqrt(max(m_sq, 0))
                c = 0.0
                
                perr = np.sqrt(np.diag(pcov))
                m_err = perr[0] / (2 * m) if m > 0 else 0
                c_err = 0.0
                alpha_err = perr[1]
            
            else:
                raise ValueError(f"Unknown fit_order: {fit_order}")
            
            # Compute R²
            if fit_order == 'quartic':
                omega_sq_fit = quartic_model(k, m**2, c**2, alpha)
            elif fit_order == 'quadratic':
                omega_sq_fit = quadratic_model(k, m**2, c**2)
            else:
                omega_sq_fit = mass_quartic_model(k, m**2, alpha)
            
            ss_res = np.sum((omega_squared - omega_sq_fit)**2)
            ss_tot = np.sum((omega_squared - np.mean(omega_squared))**2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            
        except Exception as e:
            warnings.warn(f"Fit failed: {e}. Returning default values.")
            m, c, alpha = 0.0, 0.0, 0.0
            m_err, c_err, alpha_err = 0.0, 0.0, 0.0
            r_squared = 0.0
        
        return DispersionParameters(
            mass=m,
            c=c,
            alpha=alpha,
            mass_err=m_err,
            c_err=c_err,
            alpha_err=alpha_err,
            r_squared=r_squared
        )
    
    def compute_phase_velocity(self, data: DispersionData) -> Tuple[float, float]:
        """
        Compute phase velocity from linear fit at small k.
        
        v_phase = ω/k ≈ c  (for small k)
        
        Args:
            data: DispersionData
            
        Returns:
            Tuple of (v_phase, v_phase_err)
        """
        # Use only small k values for linear regime
        k_max_linear = 0.5 * np.max(data.k)
        mask = data.k <= k_max_linear
        
        if np.sum(mask) < 2:
            return 0.0, 0.0
        
        k_linear = data.k[mask]
        omega_linear = data.omega[mask]
        
        # Linear fit: ω = v_phase * k
        try:
            slope, intercept, r_value, p_value, std_err = linregress(k_linear, omega_linear)
            return slope, std_err
        except:
            return 0.0, 0.0
    
    def compute_group_velocity(self, data: DispersionData) -> np.ndarray:
        """
        Compute group velocity v_g = dω/dk.
        
        Args:
            data: DispersionData
            
        Returns:
            Group velocity array (same shape as data.k)
        """
        if len(data.k) < 2:
            return np.zeros_like(data.k)
        
        # Numerical derivative
        v_group = np.gradient(data.omega, data.k)
        
        return v_group


# Module-level convenience function

def analyze_field_dispersion(
    field_data: np.ndarray,
    times: np.ndarray,
    grid_params,
    fit_order: str = 'quartic',
    k_range: Optional[Tuple[float, float]] = None,
    plot: bool = False
) -> Tuple[DispersionData, DispersionParameters]:
    """
    One-shot dispersion analysis of field evolution data.
    
    Args:
        field_data: Field time series (Nt, Nx) or (Nt, Nx, Ny)
        times: Time array (Nt,)
        grid_params: GridParameters
        fit_order: 'quartic', 'quadratic', or 'mass_quartic'
        k_range: Optional (k_min, k_max) for fitting
        plot: Whether to generate plots (requires matplotlib)
        
    Returns:
        Tuple of (DispersionData, DispersionParameters)
    """
    # Create analyzer
    analyzer = DispersionAnalyzer(field_data, times, grid_params)
    
    # Compute FFT
    analyzer.compute_fft()
    
    # Extract dispersion
    data = analyzer.extract_dispersion_peaks(k_range=k_range)
    
    # Fit dispersion relation
    params = analyzer.fit_dispersion_relation(data, fit_order=fit_order)
    
    # Plot if requested
    if plot:
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            # Plot 1: FFT magnitude
            k_vals, omega_vals, fft_mag = analyzer._k_values, analyzer._omega_values, analyzer._fft_result
            omega_pos_mask = omega_vals >= 0
            k_pos_mask = k_vals >= 0
            
            extent = [k_vals[k_pos_mask].min(), k_vals[k_pos_mask].max(),
                     omega_vals[omega_pos_mask].min(), omega_vals[omega_pos_mask].max()]
            
            axes[0].imshow(np.log10(fft_mag[omega_pos_mask][:, k_pos_mask] + 1e-10),
                          aspect='auto', origin='lower', extent=extent, cmap='viridis')
            axes[0].set_xlabel('k')
            axes[0].set_ylabel('ω')
            axes[0].set_title('FFT Magnitude (log scale)')
            
            # Plot 2: Dispersion relation
            axes[1].scatter(data.k, data.omega_squared, c=data.amplitude, cmap='plasma', label='Data')
            
            # Fit curve
            k_fit = np.linspace(data.k.min(), data.k.max(), 100)
            omega_sq_fit = params.mass**2 + params.c**2 * k_fit**2 + params.alpha * k_fit**4
            axes[1].plot(k_fit, omega_sq_fit, 'r-', linewidth=2, label='Fit')
            
            axes[1].set_xlabel('k')
            axes[1].set_ylabel('ω²')
            axes[1].set_title(f'Dispersion Relation (R²={params.r_squared:.3f})')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("Matplotlib not available for plotting")
    
    return data, params


if __name__ == "__main__":
    # Demonstration
    print("=" * 70)
    print("DISPERSION ANALYSIS DEMONSTRATION")
    print("=" * 70)
    
    # Generate synthetic dispersive wave packet
    print("\nGenerating dispersive wave packet...")
    
    # Parameters
    Nx = 128  # More resolution
    Nt = 256  # More time steps
    Lx = 20.0  # Larger domain
    T = 10.0   # Shorter time (to see dispersion clearly)
    
    # Grid
    x = np.linspace(0, Lx, Nx)
    t = np.linspace(0, T, Nt)
    dx = x[1] - x[0]
    dt = t[1] - t[0]
    
    # True dispersion relation: ω²(k) = m² + c²k² + αk⁴
    m_true = 0.5
    c_true = 1.0
    alpha_true = 0.05  # Smaller for clearer effect
    
    # Create a Gaussian wave packet in k-space that will disperse
    # Initial condition: Gaussian centered at k0 with significant width
    k0 = np.pi / Lx * 8  # Central wavenumber
    sigma_k = 2.0  # WIDER in k-space to excite multiple modes
    
    # k-space grid
    k_vals = 2 * np.pi * fft.fftfreq(Nx, d=dx)
    
    # Initial Gaussian in k-space
    psi_k_0 = np.exp(-(k_vals - k0)**2 / (2 * sigma_k**2))
    psi_k_0 /= np.sqrt(np.sum(np.abs(psi_k_0)**2))  # Normalize
    
    # Evolve in time with dispersion relation
    field = np.zeros((Nt, Nx))
    
    for i_t, time in enumerate(t):
        # Each k-mode evolves as exp(-i*ω(k)*t)
        omega_k = np.sqrt(m_true**2 + c_true**2 * k_vals**2 + alpha_true * k_vals**4)
        
        # Time evolution in k-space
        psi_k_t = psi_k_0 * np.exp(-1j * omega_k * time)
        
        # Transform back to real space
        psi_x_t = fft.ifft(psi_k_t)
        
        # Store real part (physical field)
        field[i_t, :] = np.real(psi_x_t)
    
    print(f"Generated wave packet: {Nt} time steps, {Nx} spatial points")
    print(f"Wave packet should disperse from center at k₀={k0:.3f}")
    
    # Mock grid parameters
    class MockGrid:
        def __init__(self):
            self.dx = dx
            self.is_1d = True
    
    grid = MockGrid()
    
    # Analyze
    print("\nAnalyzing dispersion...")
    data, params = analyze_field_dispersion(
        field, t, grid, 
        fit_order='quartic',
        k_range=(0.1, 2.0)  # Focus on relevant k range
    )
    
    print(f"\nExtracted {len(data.k)} dispersion points")
    print(f"\nFitted parameters:")
    print(params)
    
    print(f"\nTrue values:")
    print(f"  Mass gap (m):      {m_true:.6f}")
    print(f"  Phase velocity (c): {c_true:.6f}")
    print(f"  Skyrme coeff (α):   {alpha_true:.6f}")
    
    # Compute relative errors
    if params.mass > 0:
        m_error = abs(params.mass - m_true) / m_true * 100
        c_error = abs(params.c - c_true) / c_true * 100
        alpha_error = abs(params.alpha - alpha_true) / alpha_true * 100
        
        print(f"\nRelative errors:")
        print(f"  Mass gap:      {m_error:.1f}%")
        print(f"  Phase velocity: {c_error:.1f}%")
        print(f"  Skyrme coeff:   {alpha_error:.1f}%")
    
    print("\n" + "=" * 70)
    print("Demonstration complete.")
    print("=" * 70)

