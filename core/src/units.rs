//! Planck-egység konverziók. A numerikus magban a mennyiségek egy része Planck-
//! egységben kényelmesebb (M/m_P, t/t_P); a be- és kimenet mindig SI.

use crate::constants::{L_P, M_PLANCK, RHO_PLANCK, TEMP_PLANCK, T_PLANCK};

pub fn mass_to_planck(kg: f64) -> f64 {
    kg / M_PLANCK
}
pub fn mass_from_planck(m: f64) -> f64 {
    m * M_PLANCK
}
pub fn time_to_planck(s: f64) -> f64 {
    s / T_PLANCK
}
pub fn time_from_planck(t: f64) -> f64 {
    t * T_PLANCK
}
pub fn length_to_planck(m: f64) -> f64 {
    m / L_P
}
pub fn density_to_planck(kg_m3: f64) -> f64 {
    kg_m3 / RHO_PLANCK
}
pub fn temperature_to_planck(k: f64) -> f64 {
    k / TEMP_PLANCK
}
