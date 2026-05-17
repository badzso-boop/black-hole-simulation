// v3 placeholder — Island Formula (Almheiri et al. 2019)
// Az általánosított entrópia számítása: S_gen = S_BH + S_rad + S_island
// A Page-görbe teszt egyszerűsített verziót használ

use crate::black_hole::BlackHoleTrait;
use crate::error::SimulationError;

#[derive(Debug, Clone, Default)]
pub struct RadiationState {
    pub entropy: f64,
}

pub struct IslandFormula;

impl IslandFormula {
    pub fn new() -> Self {
        Self
    }

    /// Általánosított entrópia közelítés (Page-görbe teszthez)
    /// Korai idő: S ≈ S_BH (Bekenstein-Hawking)
    /// Késői idő (Page után): S csökken
    pub fn compute_generalized_entropy(
        &self,
        time: f64,
        bh: &dyn BlackHoleTrait,
        radiation: &RadiationState,
    ) -> Result<f64, SimulationError> {
        let s_bh = bh.bekenstein_entropy();
        let t_page = bh.evaporation_time() / 2.0;

        // Egyszerűsített Page-görbe: lineárisan nő majd csökken
        let s_gen = if time < t_page {
            s_bh * (time / t_page).min(1.0)
        } else {
            let decay = (time - t_page) / (bh.evaporation_time() - t_page);
            s_bh * (1.0 - decay.min(1.0))
        };

        Ok(s_gen + radiation.entropy)
    }
}

impl Default for IslandFormula {
    fn default() -> Self {
        Self::new()
    }
}
