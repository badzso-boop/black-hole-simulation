use crate::black_hole::InteriorModel;
use crate::types::InteriorKind;

/// StandardInterior — klasszikus általános relativitás: a porgömb a
/// szingularitás felé omlik, a leírás ρ = ρ_c-nél érvényét veszti.
#[derive(Debug, Clone, Default)]
pub struct StandardInterior;

impl StandardInterior {
    pub fn new() -> Self {
        Self
    }
}

impl InteriorModel for StandardInterior {
    fn kind(&self) -> InteriorKind {
        InteriorKind::Standard
    }

    fn continues_through_bounce(&self) -> bool {
        false
    }
}
