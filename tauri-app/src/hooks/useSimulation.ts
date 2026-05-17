import { useState, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";

export interface TimeStep {
  time: number;
  mass: number;
  temperature: number;
  entropy: number;
  spectrum: { frequencies: number[]; intensities: number[]; temperature: number; total_power: number };
}

export interface SimulationResults {
  schema_version: string;
  timeline: TimeStep[];
  evaporation_complete: boolean;
}

export interface CurrentState {
  running: boolean;
  step: number;
  mass: number;
  temperature: number;
  norbi_mode: boolean;
}

export function useSimulation() {
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [currentState, setCurrentState] = useState<CurrentState>({
    running: false,
    step: 0,
    mass: 0,
    temperature: 0,
    norbi_mode: false,
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = useCallback(
    async (mass: number, norbiMode: boolean, payloadJson: string = "{}") => {
      setLoading(true);
      setError(null);
      try {
        const json = await invoke<string>("run_simulation", {
          mass,
          norbi_mode: norbiMode,
          payload_json: payloadJson,
        });
        const parsed: SimulationResults = JSON.parse(json);
        setResults(parsed);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const refreshState = useCallback(async () => {
    try {
      const state = await invoke<CurrentState>("get_current_state");
      setCurrentState(state);
    } catch (_) {
      // nem kritikus
    }
  }, []);

  const toggleNorbiMode = useCallback(async (enabled: boolean) => {
    await invoke("toggle_norbi_mode", { enabled });
    setCurrentState((s) => ({ ...s, norbi_mode: enabled }));
  }, []);

  return {
    results,
    currentState,
    error,
    loading,
    runSimulation,
    refreshState,
    toggleNorbiMode,
  };
}
