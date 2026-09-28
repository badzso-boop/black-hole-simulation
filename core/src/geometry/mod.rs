//! Kvantum Oppenheimer–Snyder külső geometria és kauzalitás.
//!
//! Lewandowski–Ma–Yang–Zhang, PRL 130, 101501 (2023), arXiv:2210.02253:
//! LQC-porgömb összeomlásakor a külső metrika
//!   f(r) = 1 − 2m/r + α m²/r⁴,   m = GM/c²,   α = 16√3πγ³ℓ_P²
//! A porfelület r_b = (αm/2)^(1/3)-nél pattan vissza. M < M_min ≈ 0.83 m_P
//! esetén f > 0 mindenhol: nincs horizont (tömegrés).
//!
//! A Norbi-hipotézis kulcskérdése: eljuthat-e a visszapattanó tartomány
//! („bébiuniverzum széle") sugárzása a *külső* megfigyelőhöz?
//!
//! Analitikus tények (ezeket a kód számolja és a tesztek ellenőrzik):
//! 1. f(r_b) = 1 pontosan (mert αm² = 2m·r_b³), és r_b < r_* = (2αm)^(1/3),
//!    ahol f minimuma van. Mivel f a (0, r_*) szakaszon csökken és f(r_b) > 0,
//!    r_b < r_− : a visszapattanás a *belső* horizonton belül történik.
//! 2. Befutó Eddington–Finkelstein koordinátákban a kifelé tartó fénysugarakra
//!    dr/dv = f(r)/2. r < r_− esetén f > 0, de f(r_−) = 0 fixpont, így a sugár
//!    r_−-t csak aszimptotikusan közelíti: δ(v) = r_− − r ≈ δ_b·e^(−κ_− v).
//!    A belső (Cauchy-)horizontot v → ∞-ben lépi át — a maximális
//!    kiterjesztésben egy *másik* aszimptotikus tartomány fehérlyuk-régiójába,
//!    nem vissza az eredeti külső térbe (r > r_+).
//!
//! Következmény: az eredeti külső megfigyelő felé nincs kauzális csatorna.
//! Ez egybevág a bébiuniverzum-irodalommal (Frolov–Markov–Mukhanov 1990;
//! Chakrabarty et al. 2020; Masó-Ferrando et al. 2023): a belső tartomány
//! horizont mögött, kauzálisan leválasztva van.
//!
//! Nem modellezett alternatíva: a Husain–Kelly–Santacruz–Wilson-Ewing (2022)
//! LTB-porösszeomlásban a visszapattanó anyag lökéshullámként a *mi*
//! univerzumunkba jön ki (~M² idő alatt) — ez azonban nem bébiuniverzum, és
//! nem Hawking-szerű spektrum; a Norbi-hipotézis ezt a képet nem állítja.

use serde::{Deserialize, Serialize};

use crate::constants::{ALPHA_LMY, C, G, M_MIN_LMY};
use crate::error::SimulationError;

/// A kvantum Oppenheimer–Snyder külső metrika
#[derive(Debug, Clone, Copy)]
pub struct LmyMetric {
    /// m = GM/c² (m)
    pub m: f64,
    /// ε = α/m² (dimenziótlan) — nagy tömegre elképesztően kicsi (~1e-76 a Napra)
    pub eps: f64,
}

/// Horizontok és a visszapattanás helye (m)
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct Horizons {
    pub r_minus: f64,
    pub r_plus: f64,
    pub r_bounce: f64,
    /// δ_b = r_− − r_b > 0, kioltás nélkül számolva (a Napra ~1e-26 relatív)
    pub bounce_gap_below_inner_horizon: f64,
    /// A belső horizont felületi gravitációja κ_− = |f'(r_−)|/2 (1/m)
    pub kappa_inner: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CausalChannel {
    /// Eljut-e a visszapattanó tartomány sugárzása a külső megfigyelőhöz
    pub exists: bool,
    pub reason: String,
    pub horizons: Horizons,
    /// A tartomány széléről (r_b) induló kifelé tartó fénysugár távolsága a belső
    /// horizont alatt a numerikus integrálás végén: δ = r_− − r > 0 (m).
    /// (Nagy tömegre r_− és r_b f64-ben egyenlő, ezért a távolságot tároljuk.)
    pub edge_ray_final_gap: f64,
    /// Az integrálás hossza a belső horizont e-redőiben (κ_− v)
    pub edge_ray_efolds: f64,
}

impl LmyMetric {
    pub fn new(mass: f64) -> Self {
        let m = G * mass / (C * C);
        Self {
            m,
            eps: ALPHA_LMY / (m * m),
        }
    }

    /// f(r) — általános alak (horizontok közelében kioltásra hajlamos, ott
    /// a faktorizált alakot használjuk)
    pub fn f(&self, r: f64) -> f64 {
        let x = r / self.m;
        1.0 - 2.0 / x + self.eps / x.powi(4)
    }

    /// r_b = (αm/2)^(1/3)
    pub fn bounce_radius(&self) -> f64 {
        self.m * (self.eps / 2.0).cbrt()
    }

    /// Horizontok: x⁴ − 2x³ + ε = 0 gyökei (x = r/m), kioltásmentes fixpont-iterációval:
    ///   belső:  x = (ε/(2 − x))^(1/3)
    ///   külső:  x = 2 − ε/x³
    pub fn horizons(&self) -> Option<Horizons> {
        let eps = self.eps;
        // f minimuma x_* = (2ε)^(1/3); ha ott f ≥ 0, nincs horizont
        let x_star = (2.0 * eps).cbrt();
        if 1.0 - 2.0 / x_star + eps / x_star.powi(4) >= 0.0 {
            return None;
        }
        let mut x_m = (eps / 2.0).cbrt();
        for _ in 0..200 {
            let next = (eps / (2.0 - x_m)).cbrt();
            if (next - x_m).abs() <= 1e-16 * next {
                x_m = next;
                break;
            }
            x_m = next;
        }
        let mut x_p: f64 = 2.0;
        for _ in 0..200 {
            let next = 2.0 - eps / x_p.powi(3);
            if (next - x_p).abs() <= 1e-16 * next {
                x_p = next;
                break;
            }
            x_p = next;
        }
        // A fixpont-iteráció csak akkor konvergál, ha a gyökök jól elkülönülnek;
        // a tömegrés közelében biszekcióval pontosítunk.
        let poly = |x: f64| x.powi(4) - 2.0 * x.powi(3) + eps;
        let bisect = |mut lo: f64, mut hi: f64| {
            for _ in 0..200 {
                let mid = 0.5 * (lo + hi);
                if (poly(lo) > 0.0) == (poly(mid) > 0.0) {
                    lo = mid;
                } else {
                    hi = mid;
                }
            }
            0.5 * (lo + hi)
        };
        if poly(x_m).abs() > 1e-10 * eps || x_m >= x_star {
            x_m = bisect(0.5 * x_star, x_star);
        }
        if x_p <= x_star || poly(x_p).abs() > 1e-10 {
            x_p = bisect(x_star, 2.0);
        }
        let x_b = (eps / 2.0).cbrt();
        // δ/x_b = (2/(2 − x_−))^(1/3) − 1 = expm1(−⅓·ln1p(−x_−/2))
        let gap = x_b * (-(1.0 / 3.0) * (-x_m / 2.0).ln_1p()).exp_m1();
        // |f'(r_−)|/2 = (3m − 2r_−)/r_−²
        let r_m = x_m * self.m;
        let kappa = (3.0 * self.m - 2.0 * r_m) / (r_m * r_m);
        Some(Horizons {
            r_minus: r_m,
            r_plus: x_p * self.m,
            r_bounce: x_b * self.m,
            bounce_gap_below_inner_horizon: gap * self.m,
            kappa_inner: kappa,
        })
    }

    /// f(r) faktorizált, kioltásmentes alakban a belső horizont alatti δ = r_− − r távolságra:
    ///   r⁴f = (r − r_−)(r − r_+)(r² + b r + c),  b = r_− + r_+ − 2m,  c = αm²/(r_− r_+)
    fn f_below_inner(&self, h: &Horizons, delta: f64) -> f64 {
        let r = h.r_minus - delta;
        let alpha_m2 = self.eps * self.m.powi(4);
        let b = h.r_minus + h.r_plus - 2.0 * self.m;
        let c = alpha_m2 / (h.r_minus * h.r_plus);
        delta * (h.r_plus - r) * (r * r + b * r + c) / r.powi(4)
    }
}

/// A kauzális csatorna kiértékelése: az analitikus érvek + numerikus sugárkövetés
/// ln δ-ban (dlnδ/dv = −f/(2δ)), `n_efolds` e-redőnyi v-hosszon.
pub fn causal_channel(mass: f64) -> Result<CausalChannel, SimulationError> {
    let metric = LmyMetric::new(mass);
    let h = metric.horizons().ok_or(SimulationError::MassGap {
        mass,
        m_min: M_MIN_LMY,
    })?;

    // 1. r_b a belső horizont alatt van, és ott f > 0 (f(r_b) = 1 analitikusan)
    let below_inner = h.bounce_gap_below_inner_horizon > 0.0;

    // 2. Kifelé tartó fénysugár r_b-ről: δ(v) monoton csökken, de pozitív marad
    let n_efolds = 60.0;
    let v_end = n_efolds / h.kappa_inner;
    let n = 600;
    let dv = v_end / n as f64;
    let mut ln_delta = h.bounce_gap_below_inner_horizon.ln();
    for _ in 0..n {
        // RK4 ln δ-ban: sima, hiszen dlnδ/dv ≈ −κ_− állandó közelében
        let rate = |ld: f64| {
            let d = ld.exp();
            -metric.f_below_inner(&h, d) / (2.0 * d)
        };
        let k1 = rate(ln_delta);
        let k2 = rate(ln_delta + 0.5 * dv * k1);
        let k3 = rate(ln_delta + 0.5 * dv * k2);
        let k4 = rate(ln_delta + dv * k3);
        ln_delta += dv / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
    }
    let delta_end = ln_delta.exp();
    // δ > 0: a sugár a belső horizont alatt maradt (r_+ > r_− felett sosem jut)
    let escapes = delta_end.is_nan() || delta_end <= 0.0;

    let exists = !below_inner || escapes;
    let reason = if exists {
        "A visszapattanás a belső horizonton kívül történt — kauzális kapcsolat lehetséges".into()
    } else {
        format!(
            "A visszapattanás r_b = {:.3e} m-nél, a belső horizont (r_− = {:.3e} m) alatt \
             δ = {:.3e} m-rel történik. A kifelé tartó fénysugarak r_−-t csak aszimptotikusan \
             közelítik (δ ∝ e^(−κ_− v), κ_− = {:.3e} 1/m; {n_efolds} e-redő után δ = {:.3e} m), \
             a külső horizontot (r_+ = {:.3e} m) sosem érik el: a tartomány kauzálisan \
             le van választva a külső megfigyelőről [LMY 2023].",
            h.r_bounce,
            h.r_minus,
            h.bounce_gap_below_inner_horizon,
            h.kappa_inner,
            delta_end,
            h.r_plus
        )
    };
    Ok(CausalChannel {
        exists,
        reason,
        horizons: h,
        edge_ray_final_gap: delta_end,
        edge_ray_efolds: n_efolds,
    })
}
