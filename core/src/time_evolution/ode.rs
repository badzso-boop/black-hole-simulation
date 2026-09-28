//! Vékony réteg az `ode_solvers` Dopri5 (Dormand–Prince 5(4), adaptív) fölött.
//!
//! Megjegyzés: az ode_solvers 0.6.2 sűrű (Dense) kimenete ~1e-4 relatív hibával
//! interpolál (a stepper maga ~1e-12 pontos — ellenőrizve). Ezért itt ritka
//! (Sparse) kimenettel integrálunk kimeneti intervallumonként, így minden
//! visszaadott érték valódi lépésvégpont, interpoláció nélkül.

use ode_solvers::{Dopri5, OutputType, SVector, System};

use crate::error::SimulationError;

pub const RTOL: f64 = 1e-11;

/// Integrálás `a`-tól `b`-ig; visszaadja y(b)-t.
pub fn integrate_to<const N: usize, S>(
    system: S,
    a: f64,
    b: f64,
    y: SVector<f64, N>,
    atol: f64,
) -> Result<SVector<f64, N>, SimulationError>
where
    S: System<f64, SVector<f64, N>>,
{
    if a == b {
        return Ok(y);
    }
    let span = (b - a).abs();
    let mut stepper = Dopri5::from_param(
        system,
        a,
        b,
        span,
        y,
        RTOL,
        atol,
        0.9,
        0.04,
        0.2,
        10.0,
        span,
        0.0,
        1_000_000,
        1000,
        OutputType::Sparse,
    );
    stepper
        .integrate()
        .map_err(|e| SimulationError::IntegrationFailed {
            reason: format!("{e:?}"),
        })?;
    stepper
        .y_out()
        .last()
        .copied()
        .ok_or_else(|| SimulationError::IntegrationFailed {
            reason: "üres kimenet".into(),
        })
}

/// Integrálás egy rácson: visszaadja y-t minden rácspontban (grid[0] = kezdőpont).
pub fn integrate_on_grid<const N: usize, S>(
    system: &S,
    grid: &[f64],
    y0: SVector<f64, N>,
    atol: f64,
) -> Result<Vec<SVector<f64, N>>, SimulationError>
where
    S: System<f64, SVector<f64, N>> + Clone,
{
    let mut out = Vec::with_capacity(grid.len());
    let mut y = y0;
    out.push(y);
    for w in grid.windows(2) {
        y = integrate_to(system.clone(), w[0], w[1], y, atol)?;
        out.push(y);
    }
    Ok(out)
}
