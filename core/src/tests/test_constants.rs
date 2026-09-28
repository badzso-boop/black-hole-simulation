#[cfg(test)]
mod tests {
    use crate::constants::*;
    use approx::assert_relative_eq;

    #[test]
    fn hbar_is_h_over_two_pi() {
        assert_relative_eq!(HBAR, H_PLANCK / (2.0 * PI), max_relative = 1e-15);
    }

    #[test]
    fn planck_units_follow_from_codata() {
        assert_relative_eq!(L_P, (HBAR * G / C.powi(3)).sqrt(), max_relative = 1e-14);
        assert_relative_eq!(M_PLANCK, (HBAR * C / G).sqrt(), max_relative = 1e-14);
        assert_relative_eq!(T_PLANCK, L_P / C, max_relative = 1e-14);
        assert_relative_eq!(TEMP_PLANCK, M_PLANCK * C * C / K_B, max_relative = 1e-14);
        assert_relative_eq!(RHO_PLANCK, C.powi(5) / (HBAR * G * G), max_relative = 1e-14);
        // NIST CODATA 2022 publikált értékei (a mért G bizonytalanságán belül)
        assert_relative_eq!(L_P, 1.616255e-35, max_relative = 1e-6);
        assert_relative_eq!(M_PLANCK, 2.176434e-8, max_relative = 1e-6);
        assert_relative_eq!(T_PLANCK, 5.391247e-44, max_relative = 1e-6);
        assert_relative_eq!(TEMP_PLANCK, 1.416784e32, max_relative = 1e-6);
    }

    #[test]
    fn lqc_critical_density_is_041_planck() {
        let expected = 3f64.sqrt() / (32.0 * PI * PI * GAMMA_BI.powi(3)) * RHO_PLANCK;
        assert_relative_eq!(RHO_CRIT_LQC, expected, max_relative = 1e-14);
        assert_relative_eq!(RHO_CRIT_LQC / RHO_PLANCK, 0.4094, max_relative = 1e-3);
    }

    #[test]
    fn lmy_alpha_and_mass_gap() {
        let alpha = 16.0 * 3f64.sqrt() * PI * GAMMA_BI.powi(3) * L_P * L_P;
        assert_relative_eq!(ALPHA_LMY, alpha, max_relative = 1e-14);
        let m_min = 4.0 * alpha.sqrt() * C * C / (3.0 * 3f64.sqrt() * G);
        assert_relative_eq!(M_MIN_LMY, m_min, max_relative = 1e-14);
        assert_relative_eq!(M_MIN_LMY / M_PLANCK, 0.8314, max_relative = 1e-3);
    }

    #[test]
    fn wien_constant() {
        // x = 2.821439... a ν³/(eˣ−1) maximuma
        assert_relative_eq!(
            WIEN_FREQ,
            2.821_439_372_122_079 * K_B / H_PLANCK,
            max_relative = 1e-12
        );
    }
}
