"""
Tests for Reincarnation Dynamics Module

Test suite for reincarnation_dynamics.py covering:
1. Soul state creation and management
2. Life cycle evolution
3. Death transition
4. Rebirth refocusing
5. Q_H conservation
6. Crisis node detection
7. Multi-life trajectories

Author: FIRM-Core Development Team
Date: 2025-10-08
Version: 1.0.0
"""

import unittest
import numpy as np
from FIRM_dsl.reincarnation_dynamics import (
    SoulState,
    LifeCycle,
    ReincarnationSimulator
)


class TestSoulState(unittest.TestCase):
    """Test Soul state data structure."""
    
    def test_creation(self):
        """Test creating Soul state."""
        Psi = np.array([1+0j, 0+1j, 1+1j])
        state = SoulState(
            Psi=Psi, Q_H=1.0, phase=0.5, energy=1.0,
            time=0.0, coherence=0.8, grace_coupling=0.5
        )
        
        self.assertEqual(state.Q_H, 1.0)
        self.assertEqual(state.coherence, 0.8)
    
    def test_string_representation(self):
        """Test string formatting."""
        Psi = np.array([1+0j])
        state = SoulState(
            Psi=Psi, Q_H=1.5, phase=0.0, energy=1.0,
            time=5.0, coherence=0.7, grace_coupling=0.3
        )
        string = str(state)
        self.assertIn("t=5.00", string)
        self.assertIn("Q_H=1.500", string)


class TestLifeCycle(unittest.TestCase):
    """Test life cycle data structure."""
    
    def test_creation(self):
        """Test creating life cycle."""
        Psi = np.array([1+0j])
        initial = SoulState(Psi=Psi, Q_H=1.0, phase=0.0, energy=1.0,
                           time=0.0, coherence=0.8, grace_coupling=0.5)
        final = SoulState(Psi=Psi, Q_H=1.0, phase=0.1, energy=0.5,
                         time=10.0, coherence=0.6, grace_coupling=0.7)
        
        cycle = LifeCycle(
            t_birth=0.0, t_death=10.0, t_rebirth=12.0,
            initial_state=initial, final_state=final,
            Q_H_conservation_error=0.001
        )
        
        self.assertEqual(cycle.t_birth, 0.0)
        self.assertEqual(cycle.t_death, 10.0)
        self.assertAlmostEqual(cycle.Q_H_conservation_error, 0.001)


class TestReincarnationSimulator(unittest.TestCase):
    """Test reincarnation simulator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulator = ReincarnationSimulator()
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        self.assertIsNotNone(self.simulator)
    
    def test_create_initial_soul(self):
        """Test creating initial Soul."""
        soul = self.simulator.create_initial_soul(Q_H=1.5, coherence=0.7)
        
        self.assertEqual(soul.Q_H, 1.5)
        self.assertEqual(soul.coherence, 0.7)
        self.assertIsInstance(soul.Psi, np.ndarray)
    
    def test_evolve_soul(self):
        """Test evolving Soul state."""
        initial = self.simulator.create_initial_soul(Q_H=1.0, coherence=0.8)
        trajectory = self.simulator.evolve_soul(initial, t_final=5.0, dt=0.5)
        
        # Should have multiple states
        self.assertGreater(len(trajectory), 1)
        
        # First state should be initial
        self.assertEqual(trajectory[0].time, initial.time)
        
        # Last state should be near t_final
        self.assertLess(abs(trajectory[-1].time - 5.0), 1.0)
    
    def test_death_transition(self):
        """Test death transition."""
        death_state = self.simulator.create_initial_soul(Q_H=1.0, coherence=0.8)
        post_death = self.simulator.death_transition(death_state, transition_time=1.0)
        
        # Coherence should drop
        self.assertLess(post_death.coherence, death_state.coherence)
        
        # Q_H should be preserved
        self.assertEqual(post_death.Q_H, death_state.Q_H)
        
        # Time should advance
        self.assertEqual(post_death.time, death_state.time + 1.0)
    
    def test_rebirth_refocusing(self):
        """Test rebirth refocusing."""
        post_death = self.simulator.create_initial_soul(Q_H=1.0, coherence=0.1)
        rebirth_state = self.simulator.rebirth_refocusing(post_death, refocus_time=2.0)
        
        # Coherence should rebuild
        self.assertGreater(rebirth_state.coherence, post_death.coherence)
        
        # Q_H should be preserved
        self.assertEqual(rebirth_state.Q_H, post_death.Q_H)
        
        # Time should advance
        self.assertEqual(rebirth_state.time, post_death.time + 2.0)
    
    def test_Q_H_conservation_through_transition(self):
        """Test that Q_H is conserved through death/rebirth."""
        initial = self.simulator.create_initial_soul(Q_H=1.5, coherence=0.8)
        post_death = self.simulator.death_transition(initial)
        rebirth = self.simulator.rebirth_refocusing(post_death)
        
        # Q_H should be exactly preserved
        self.assertEqual(initial.Q_H, post_death.Q_H)
        self.assertEqual(post_death.Q_H, rebirth.Q_H)
    
    def test_detect_crisis_nodes(self):
        """Test crisis node detection."""
        initial = self.simulator.create_initial_soul(Q_H=1.0, coherence=0.8)
        trajectory = self.simulator.evolve_soul(initial, t_final=10.0, dt=0.1)
        
        crisis_nodes = self.simulator.detect_crisis_nodes(trajectory, threshold=0.1)
        
        # Should be a list
        self.assertIsInstance(crisis_nodes, list)
        
        # Each entry should be a time value
        for t in crisis_nodes:
            self.assertIsInstance(t, (float, np.floating))
    
    def test_simulate_life_cycle(self):
        """Test complete life cycle simulation."""
        cycle = self.simulator.simulate_life_cycle(
            initial_Q_H=1.0,
            life_duration=5.0
        )
        
        self.assertIsInstance(cycle, LifeCycle)
        
        # Check times are sensible
        self.assertEqual(cycle.t_birth, 0.0)
        self.assertGreater(cycle.t_death, cycle.t_birth)
        self.assertGreater(cycle.t_rebirth, cycle.t_death)
        
        # Check states exist
        self.assertIsNotNone(cycle.initial_state)
        self.assertIsNotNone(cycle.final_state)
        self.assertIsNotNone(cycle.next_state)
        
        # Check Q_H conservation
        self.assertLess(cycle.Q_H_conservation_error, 0.01)
    
    def test_multi_life_trajectory(self):
        """Test multi-life simulation."""
        cycles = self.simulator.simulate_multi_life_trajectory(
            num_lives=3,
            initial_Q_H=1.0,
            life_duration=5.0
        )
        
        self.assertEqual(len(cycles), 3)
        
        # Check Q_H conservation across all lives
        for cycle in cycles:
            self.assertLess(cycle.Q_H_conservation_error, 0.01)
        
        # Check continuity
        for i in range(len(cycles) - 1):
            # Next life should start from previous rebirth
            self.assertAlmostEqual(
                cycles[i].next_state.Q_H,
                cycles[i+1].initial_state.Q_H,
                places=10
            )


class TestPhysicalConsistency(unittest.TestCase):
    """Test physical consistency of reincarnation dynamics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulator = ReincarnationSimulator()
    
    def test_energy_decreases_during_death(self):
        """Test that energy decreases during death."""
        death_state = self.simulator.create_initial_soul(Q_H=1.0, coherence=0.8)
        post_death = self.simulator.death_transition(death_state)
        
        self.assertLess(post_death.energy, death_state.energy)
    
    def test_coherence_cycle(self):
        """Test coherence evolution through full cycle."""
        cycle = self.simulator.simulate_life_cycle(initial_Q_H=1.0)
        
        # Coherence should drop from initial to final
        self.assertLess(cycle.final_state.coherence, cycle.initial_state.coherence)
        
        # Coherence should rebuild at rebirth
        self.assertGreater(cycle.next_state.coherence, cycle.final_state.coherence)
    
    def test_phase_continuity(self):
        """Test that phase evolves continuously."""
        initial = self.simulator.create_initial_soul(Q_H=1.0, coherence=0.8)
        trajectory = self.simulator.evolve_soul(initial, t_final=5.0, dt=0.1)
        
        # Check phase doesn't jump discontinuously
        for i in range(1, len(trajectory)):
            phase_diff = abs(trajectory[i].phase - trajectory[i-1].phase)
            # Allow for phase wrapping
            phase_diff = min(phase_diff, 2*np.pi - phase_diff)
            self.assertLess(phase_diff, np.pi)  # No jumps larger than π
    
    def test_Q_H_exact_conservation(self):
        """Test that Q_H is exactly conserved (within numerical precision)."""
        cycle = self.simulator.simulate_life_cycle(initial_Q_H=1.0)
        
        # Q_H should be exactly preserved (to machine precision)
        self.assertEqual(cycle.Q_H_conservation_error, 0.0)
    
    def test_grace_coupling_increases_at_death(self):
        """Test that Grace coupling increases during death transition."""
        death_state = self.simulator.create_initial_soul(Q_H=1.0, coherence=0.8)
        death_state.grace_coupling = 0.3  # Set moderate coupling
        
        post_death = self.simulator.death_transition(death_state)
        
        # Grace coupling should spike
        self.assertGreater(post_death.grace_coupling, death_state.grace_coupling)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

