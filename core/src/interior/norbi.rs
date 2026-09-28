use crate::black_hole::InteriorModel;
use crate::types::InteriorKind;

/// NorbiInterior — LQC effektív dinamika: ρ_c-nél kvantum-visszapattanás,
/// utána a porgömb tágul (a Norbi-hipotézis „bébiuniverzuma").
/// A visszapattanás ott történik, ahol a dinamika előírja — nem a 0. lépésben.
#[derive(Debug, Clone, Default)]
pub struct NorbiInterior;

impl NorbiInterior {
    pub fn new() -> Self {
        Self
    }
}

impl InteriorModel for NorbiInterior {
    fn kind(&self) -> InteriorKind {
        InteriorKind::Norbi
    }

    fn continues_through_bounce(&self) -> bool {
        true
    }
}
