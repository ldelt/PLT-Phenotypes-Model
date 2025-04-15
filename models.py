import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp


# Formulas for determining constants
def calculate_k_inh(IC50_ilo, h_ilo, ADP, EC50):
    return IC50_ilo

def calculate_k_with_inh(k_max, ADP, h_k, EC50, ilo, ki):
    return k_max * (1 / ((1 + (ilo / ki)))) * (ADP ** h_k) / (ADP ** h_k + EC50 ** h_k) # k с учетом ki

def calculate_k_simple(k_max, concentration, h_k, EC50):
    return k_max * (concentration ** h_k) / (concentration ** h_k + EC50 ** h_k) # k без учета ki (concentration - ADP или Ilo)

def calculete_reverse(k_max, IC50, h_k, ADP):
    return k_max * (IC50 ** h_k) / (IC50 ** h_k + ADP ** h_k) # k из IC50

# ODE System
def system(t, y, k1, k2, k3, k5, k6, k7, k12, k21, k11):
    N_rest, N_sph, N_inh, N_gp, N_agg, N_exh = y
    dN_rest_dt = k21 * N_inh + k11 * N_exh - k12 * N_rest - k1 * N_rest
    dN_sph_dt = k1 * N_rest - k2 * N_sph - k5 * N_sph
    dN_inh_dt = k12 * N_rest - k21 * N_inh
    dN_gp_dt = k2 * N_sph - k3 * (N_gp ** 2) - k6 * N_gp
    dN_agg_dt = k3 * (N_gp ** 2) - k7 * N_agg
    dN_exh_dt = k5 * N_sph + k6 * N_gp + k7 * N_agg - k11 * N_exh
    return np.array([dN_rest_dt, dN_sph_dt, dN_inh_dt, dN_gp_dt, dN_agg_dt, dN_exh_dt])

# Limitations on negative values
def trim_negative_values(t, y, k1, k2, k3, k5, k6, k7, k12, k21, k11):
    return np.minimum(y, 0)

def event_negative(t, y, k1, k2, k3, k5, k6, k7, k12, k21, k11):
    return np.min(y) - 1e-6

event_negative.terminal = True
event_negative.direction = -1

# Solution of ODE system
def calculate_concentrations(points, max_time, y0, params):
    results = pd.DataFrame()
    current_y0 = np.array(y0)

    for i in range(len(points)):
        ADP = points[i][1]
        ilo = points[i][2]

        # Calculate all constants from params
        ki_1 = calculate_k_inh(params['IC50_k1_ilo'], params['h_k1_ilo'], ADP, params['EC50_k1'])
        k1 = calculate_k_with_inh(params['k1_max'], ADP, params['h_k1'], params['EC50_k1'], ilo, ki_1)

        ki_2 = calculate_k_inh(params['IC50_k2_ilo'], params['h_k2_ilo'], ADP, params['EC50_k2'])
        k2 = calculate_k_with_inh(params['k2_max'], ADP, params['h_k2'], params['EC50_k2'], ilo, ki_2)

        k3 = calculate_k_simple(params['k3_max'], ADP, params['h_k3'], params['EC50_k3'])
        k12 = calculate_k_simple(params['k12_max'], ilo, params['h_k12'], params['EC50_k12'])
        k21 = calculate_k_simple(params['k21_max'], ADP, params['h_k21'], params['EC50_k21'])

        ki_5 = calculate_k_inh(params['IC50_k5_ADP'], params['h_k5_ADP'], ilo, params['EC50_k5_ilo'])
        k5 = (
            calculate_k_with_inh(params['k5_max_a'], ilo, params['h_k5_ilo'], params['EC50_k5_ilo'], ADP, ki_5) +
            calculete_reverse(params['k5_max'], params['IC50_k5_ADP'], params['h_k5_ADP'], ADP)
        )

        ki_6 = calculate_k_inh(params['IC50_k6_ADP'], params['h_k6_ADP'], ilo, params['EC50_k6_ilo'])
        k6 = (
            calculate_k_with_inh(params['k6_max_a'], ilo, params['h_k6_ilo'], params['EC50_k6_ilo'], ADP, ki_6) +
            calculete_reverse(params['k6_max'], params['IC50_k6_ADP'], params['h_k6_ADP'], ADP)
        )

        ki_7 = calculate_k_inh(params['IC50_k5_ADP'], params['h_k5_ADP'], ilo, params['EC50_k5_ilo'])
        k7 = (
            calculate_k_with_inh(params['k7_max_a'], ilo, params['h_k7_ilo'], params['EC50_k7_ilo'], ADP, ki_7) +
            calculete_reverse(params['k7_max'], params['IC50_k7_ADP'], params['h_k7_ADP'], ADP)
        )

        k11 = params['k11_max']

        # Time parameters
        start = points[i][0]
        end = points[i + 1][0] if i < len(points) - 1 else max_time
        t_span = (start, end)
        t_eval = np.linspace(start, end, end - start + 1)

        # System solution
        sol = solve_ivp(
            fun=system,
            t_span=t_span,
            y0=current_y0,
            method='LSODA',
            t_eval=t_eval,
            args=(k1, k2, k3, k5, k6, k7, k12, k21, k11),
            events=event_negative
        )

        df = pd.DataFrame(sol.y.T, columns=['N_rest', 'N_sph', 'N_inh', 'N_gp', 'N_agg', 'N_exh'])
        df['Time'] = sol.t
        current_y0 = sol.y.T[-1]

        results = pd.concat([results, df], axis=0)

    return results.reset_index(drop=True)