use crate::constants::{C, G, HBAR, K_B, L_P, PI, SPECTRUM_BINS};
use crate::quantum::lqc::LQCEquation;
use crate::radiation::spectrum::{peak_frequency, planck_spectrum};
use crate::types::{BabyUniverseState, BreakupEvent, InternalObjectData};

#[derive(Debug, Clone)]
pub struct BabyUniverse {
    pub scale_factor: f64,    // dimenzió nélküli tágulási faktor
    pub expansion_rate: f64,  // H_belső (1/s)
    pub internal_density: f64, // kg/m³
    pub total_energy: f64,    // J
    pub age: f64,             // s
    pub absorbed_energy: f64, // beeső anyagból
    h_inf: f64,               // a visszapattanáskori csúcs-Hubble-ráta (1/s), rögzítve
}

impl BabyUniverse {
    /// Kvantumvisszapattanás után azonnal létrejön.
    /// Az inflációs Hubble-ráta (H_inf) nem szabadon választott konstans, hanem
    /// az LQC-egyenlet saját maximuma — lásd `LQCEquation::max_bounce_hubble_rate`.
    pub fn new(initial_density: f64) -> Self {
        let h_inf = LQCEquation::new().max_bounce_hubble_rate();
        Self {
            scale_factor: L_P,
            expansion_rate: h_inf,
            internal_density: initial_density,
            total_energy: initial_density * L_P.powi(3) * C * C,
            age: 0.0,
            absorbed_energy: 0.0,
            h_inf,
        }
    }

    /// Tágulási lépés — a(t) = a₀ · e^(H_inf · t)
    pub fn evolve(&mut self, dt: f64) {
        self.age += dt;
        self.scale_factor *= (self.expansion_rate * dt).exp();
        // Sűrűség csökken a tágulással: ρ ∝ a⁻³
        let volume_ratio = (self.expansion_rate * dt * 3.0).exp();
        self.internal_density /= volume_ratio;
        // Hubble-paraméter csökken (standard kozmológia: H(t) = H_inf / (1 + t·H_inf))
        self.expansion_rate = self.h_inf / (1.0 + self.age * self.h_inf);
    }

    /// Beeső anyag energiájának integrálása a belső univerzumba
    pub fn absorb_energy(&mut self, energy: f64) {
        self.absorbed_energy += energy;
        self.total_energy += energy;
        // Az energia részlegesen sűrűségbe megy
        let v = self.scale_factor.powi(3);
        if v > 0.0 {
            self.internal_density += energy / (v * C * C);
        }
    }

    pub fn hubble_parameter(&self) -> f64 {
        self.expansion_rate
    }

    /// Szétszakadási ráta — a belső szélén szétszakadó anyag rátája
    pub fn edge_breakup_rate(&self) -> f64 {
        // Az a skálafaktor szélén v_tágulás = H * r
        // Szétszakadás ha v > c → e_tidal > e_bind
        // Egyszerűsített: ráta ∝ H² * a
        self.expansion_rate.powi(2) * self.scale_factor
    }

    /// Közös tidal-energia / önkötési-energia számítás.
    /// E_tidal = 0.5 · m · H² · r²  (a tágulási szélen ható árapály-energia)
    /// E_bind  = 3Gm² / (5R)         (a tömeg saját gravitációs kötési energiája,
    ///                                homogén gömbre — Newton-i közelítés)
    fn tidal_and_binding(&self, mass: f64, obj_radius: f64, r: f64) -> (f64, f64) {
        let e_tidal = 0.5 * mass * self.expansion_rate.powi(2) * r.powi(2);
        let e_bind = if obj_radius > 0.0 {
            3.0 * G * mass.powi(2) / (5.0 * obj_radius)
        } else {
            f64::MAX
        };
        (e_tidal, e_bind)
    }

    /// Szétszakadás feltételének ellenőrzése egy belső objektumra
    pub fn check_breakup(
        &self,
        obj: &InternalObjectData,
        current_time: f64,
    ) -> Option<BreakupEvent> {
        let r = (obj.position[0].powi(2) + obj.position[1].powi(2) + obj.position[2].powi(2))
            .sqrt();

        let (e_tidal, e_bind) = self.tidal_and_binding(obj.mass, obj.radius, r);

        if e_tidal > e_bind {
            // A belső pozíciót az eseményhorizonton lévő pontra vetítjük
            let norm = if r > 0.0 { r } else { 1.0 };
            Some(BreakupEvent {
                released_energy: e_tidal - e_bind,
                position_on_horizon: [
                    obj.position[0] / norm,
                    obj.position[1] / norm,
                    obj.position[2] / norm,
                ],
                time: current_time,
            })
        } else {
            None
        }
    }

    /// A bébiuniverzum teljes tömegtartalmának (E_total/c²) [0,1] hányada, ami
    /// a jelenlegi tágulási szélen ténylegesen szétszakad: e_tidal / (e_tidal + e_bind).
    /// A tömeg saját sugarát a jelenlegi belső sűrűségből becsüljük
    /// (R = (3m / 4πρ)^(1/3)) — ez adja a csatolási arányt (α) a kevert
    /// Hawking/él-spektrumhoz, a korábbi, le nem vezetett energiaarány helyett.
    pub fn breakup_fraction(&self) -> f64 {
        let mass = (self.total_energy / (C * C)).max(0.0);
        if mass <= 0.0 || self.internal_density <= 0.0 {
            return 0.0;
        }
        let obj_radius = (3.0 * mass / (4.0 * PI * self.internal_density)).cbrt();
        let (e_tidal, e_bind) = self.tidal_and_binding(mass, obj_radius, self.scale_factor);
        if e_tidal + e_bind > 0.0 {
            (e_tidal / (e_tidal + e_bind)).clamp(0.0, 1.0)
        } else {
            0.0
        }
    }

    /// A bébiuniverzum de Sitter-szerű (exponenciális) tágulásának
    /// Gibbons–Hawking-hőmérséklete: T = ħH / (2πk_B).
    /// [GH77] Gibbons & Hawking (1977): kozmológiai eseményhorizontnak is van
    /// sugárzási hőmérséklete, pontosan úgy, mint a fekete lyuk horizontjának.
    pub fn edge_temperature(&self) -> f64 {
        HBAR * self.expansion_rate / (2.0 * PI * K_B)
    }

    /// A belső tágulás szélén szétszakadó anyag sugárzási spektruma —
    /// valódi Planck-spektrum az `edge_temperature()` hőmérsékleten,
    /// a hozzá tartozó (Wien-törvény szerinti) frekvenciatengelyen.
    pub fn edge_radiation_spectrum(&self) -> Vec<f64> {
        let temp = self.edge_temperature();
        self.edge_radiation_frequencies()
            .iter()
            .map(|&freq| planck_spectrum(freq, temp).unwrap_or(0.0))
            .collect()
    }

    /// Az `edge_radiation_spectrum()` bin-jeihez tartozó frekvenciák (Hz).
    pub fn edge_radiation_frequencies(&self) -> Vec<f64> {
        let temp = self.edge_temperature();
        let freq_max = peak_frequency(temp) * 10.0;
        let df = freq_max / SPECTRUM_BINS as f64;
        (0..SPECTRUM_BINS).map(|i| (i as f64 + 0.5) * df).collect()
    }

    /// A visszapattanás utáni tranziens finom (Planck-idő nagyságrendű) felbontásban.
    ///
    /// A külső Hawking-elpárlás szemiklasszikus közelítése (`t_evap ∝ M³`) csak addig
    /// érvényes, amíg a görbület távol van a Planck-skálától — pont a visszapattanásnál
    /// lép ki ebből az érvényességi tartományból. A bébiuniverzum saját tágulása ezért
    /// nem a külső elpárlási óra (`dt = t_evap/lépésszám`) szerint, hanem a saját,
    /// Planck-idő nagyságrendű óráján halad — ez a kettő időskála szétválasztása
    /// (proper time vs. külső koordináta-idő) általános relativitáselméleti alapokon
    /// áll, nem a Norbi-hipotézis specifikus feltevése.
    ///
    /// Visszaadja az állapotok sorozatát: index 0 = közvetlenül a visszapattanás után,
    /// mielőtt bármilyen tágulás történt volna.
    pub fn post_bounce_transient(
        initial_density: f64,
        n_steps: usize,
        dt_internal: f64,
    ) -> Vec<BabyUniverseState> {
        let mut bu = BabyUniverse::new(initial_density);
        let mut trace = Vec::with_capacity(n_steps + 1);
        trace.push(bu.to_state());
        for _ in 0..n_steps {
            bu.evolve(dt_internal);
            trace.push(bu.to_state());
        }
        trace
    }

    pub fn to_state(&self) -> BabyUniverseState {
        BabyUniverseState {
            scale_factor: self.scale_factor,
            expansion_rate: self.expansion_rate,
            internal_density: self.internal_density,
            edge_breakup_rate: self.edge_breakup_rate(),
            total_energy: self.total_energy,
            age: self.age,
            breakup_fraction: self.breakup_fraction(),
        }
    }
}
