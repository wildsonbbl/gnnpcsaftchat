"helper for plotting"

import uuid
from typing import List, Optional

import numpy as np
from gnnepcsaft.epcsaft.epcsaft_feos import (
    mix_den_feos,
    phase_diagram_feos,
    pure_den_feos,
    pure_h_lv_feos,
    pure_surface_tension_feos,
    pure_vp_feos,
)
from gnnepcsaft_mcp_server.utils import predict_epcsaft_parameters


def plot_pure_density(smiles: str, t_min: float, t_max: float, pressure: float):
    """
    When asked, use this tool to show the user a plot of density (mol/m³).
    To show the plot, answer the user with the exact content from
    the result part of this tool.

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate density (mol/m³)
      t_max (float): maximun temperature (K) to calculate density (mol/m³)
      pressure (float): system pressure (Pa)

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = predict_epcsaft_parameters(smiles)

    densities = [
        pure_den_feos(parameters=parameters, state=[T, pressure]) for T in temperatures
    ]

    data = [[temperatures.tolist(), densities], [[], []]]
    plot_id = f"den_plot_{uuid.uuid4().hex}"

    return f"""
    <div class="col-lg">
    <div id="{plot_id}" alt="Density plot (mol/m³)"></div>
    <script>
    getplot({data},0,"Liquid Density (mol/m³)","{plot_id}");
    </script>
    </div>
    """


def plot_pure_vapor_pressure(smiles: str, t_min: float, t_max: float):
    """
    When asked, use this tool to show the user a plot of vapor pressure (Pa).
    To show the plot, answer the user with the exact content from
    the result part of this tool.

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate vapor pressure (Pa)
      t_max (float): maximun temperature (K) to calculate vapor pressure (Pa)

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = predict_epcsaft_parameters(smiles)

    vapor_pressures = [
        pure_vp_feos(parameters=parameters, state=[T]) for T in temperatures
    ]

    data = [[temperatures.tolist(), vapor_pressures], [[], []]]
    plot_id = f"vp_plot_{uuid.uuid4().hex}"

    return f"""
    <div class="col-lg">
    <div id="{plot_id}" alt="Vapor pressure (Pa) plot"></div>
    <script>
    getplot({data},0,"Vapor Pressure (Pa)","{plot_id}");
    </script>
    </div>
    """


def plot_pure_h_lv(smiles: str, t_min: float, t_max: float):
    """
    When asked, use this tool to show the user a plot of enthalpy of vaporization (kJ/mol).
    To show the plot, answer the user with the exact content from
    the result part of this tool.

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate enthalpy of vaporization (kJ/mol)
      t_max (float): maximun temperature (K) to calculate enthalpy of vaporization (kJ/mol)

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = predict_epcsaft_parameters(smiles)

    h_lv = [pure_h_lv_feos(parameters=parameters, state=[T]) for T in temperatures]

    data = [[temperatures.tolist(), h_lv], [[], []]]
    plot_id = f"h_lv_plot_{uuid.uuid4().hex}"

    return f"""
    <div class="col-lg">
    <div id="{plot_id}" alt="Enthalpy of vaporization (kJ/mol) plot"></div>
    <script>
    getplot({data},0,"Enthalpy of vaporization (kJ/mol)","{plot_id}");
    </script>
    </div>
    """


def plot_pure_surface_tension(smiles: str, t_min: float):
    """
    When asked, use this tool to show the user a plot of Surface Tension (mN/m)
    from t_min up to the critical temperature.
    To show the plot, answer the user with the exact content from
    the result part of this tool.

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate Surface Tension (mN/m)

    """

    parameters = predict_epcsaft_parameters(smiles)

    st, temperatures = pure_surface_tension_feos(parameters=parameters, state=[t_min])

    data = [[temperatures.tolist(), st.tolist()], [[], []]]
    plot_id = f"st_plot_{uuid.uuid4().hex}"

    return f"""
    <div class="col-lg">
    <div id="{plot_id}" alt="Surface Tension (mN/m) plot"></div>
    <script>
    getplot({data},0,"Surface Tension (mN/m)","{plot_id}");
    </script>
    </div>
    """


def plot_pure_phase_diagram_t_rho(smiles: str, t_min: float):
    """
    When asked, use this tool to show the user a pure-component
    temperature (K) vs density (mol/m³) phase diagram
    from t_min up to the critical temperature.
    To show the plot, answer the user with the exact content from
    the result part of this tool.

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate phase diagram

    """

    parameters = predict_epcsaft_parameters(smiles)

    output = phase_diagram_feos(parameters=parameters, state=[t_min])

    data = [output["temperature"], output["density liquid"], output["density vapor"]]
    plot_id = f"t_rho_diagram_{uuid.uuid4().hex}"

    return f"""
    <div class="col-lg">
    <div id="{plot_id}" alt="Phase diagram plot"></div>
    <script>
    get_phase_diagram({data},0,"Temperature (K)","{plot_id}");
    </script>
    </div>
    """


def plot_mix_density(
    smiles_list: List[str],
    t_min: float,
    t_max: float,
    pressure: float,
    mole_fractions: List[float],
    kij_matrix: Optional[List[List[float]]],
):
    """
    When asked, use this tool to show the user a plot of density (mol/m³) for a mixture.
    To show the plot, answer the user with the exact content from
    the result part of this tool.

    Args:
      smiles_list (List[str]): List of mixture SMILES.
      t_min (float): minimum temperature (K) to calculate density (mol/m³)
      t_max (float): maximun temperature (K) to calculate density (mol/m³)
      pressure (float): system pressure (Pa)
      mole_fractions (List[float]): mole fractions list
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = [predict_epcsaft_parameters(smiles) for smiles in smiles_list]

    densities = [
        mix_den_feos(
            parameters=parameters,
            state=[T, pressure, *mole_fractions],
            kij_matrix=kij_matrix,
        )
        for T in temperatures
    ]

    data = [[temperatures.tolist(), densities], [[], []]]
    plot_id = f"den_plot_{uuid.uuid4().hex}"

    return f"""
    <div class="col-lg">
    <div id="{plot_id}" alt="Density plot (mol/m³)"></div>
    <script>
    getplot({data},0,"Liquid Density (mol/m³)","{plot_id}");
    </script>
    </div>
    """
