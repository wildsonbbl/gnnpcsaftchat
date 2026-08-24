"helper for plotting pure"

import json
import uuid

from gnnepcsaft_mcp_server.utils_data import (
    retrieve_rho_pure_data,
    retrieve_st_pure_data,
    retrieve_vp_pure_data,
)
from gnnepcsaft_mcp_server.utils_pure import (
    pure_den,
    pure_h_lv,
    pure_phase_diagram,
    pure_surface_tension,
    pure_vp,
)

from .core import (
    MN_PER_N,
    PA_PER_KPA,
    _experimental_plot_data,
    _make_plot_response,
)


def plot_pure_density(
    smiles: str, t_min: float, t_max: float, pressure: float, npoints: int = 100
):
    """
    When asked, use this tool to show the user a plot of density (mol/m³).

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate density (mol/m³)
      t_max (float): maximun temperature (K) to calculate density (mol/m³)
      pressure (float): system pressure (Pa)
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """

    temperatures, densities = pure_den(
        smiles=smiles,
        min_temp=t_min,
        max_temp=t_max,
        pressure=pressure,
        npoints=npoints,
    )
    exp_data = retrieve_rho_pure_data(smiles=smiles, pressure=pressure / PA_PER_KPA)

    plot_data = {"temperatures": temperatures, "pure_densities": densities}
    data = {
        "GNN": [temperatures, densities],
        "legends": [
            "GNN",
            "GNN",
            "ThermoML Archive**",
        ],
        "TML": _experimental_plot_data(exp_data),
    }
    plot_id = f"den_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Density plot (mol/m³)"></div>
    <script>
    getplot(
      {json.dumps(data)},
      "Temperature (K)",
      "Density (mol/m³)",
      "Density at P={pressure} Pa",
      "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="density",
        data=plot_data,
        html=html,
        message="Density plot generated successfully.",
    )


def plot_pure_vapor_pressure(
    smiles: str, t_min: float, t_max: float, npoints: int = 100
):
    """
    When asked, use this tool to show the user a plot of vapor pressure (Pa).

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate vapor pressure (Pa)
      t_max (float): maximun temperature (K) to calculate vapor pressure (Pa)
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """

    temperatures, vapor_pressures = pure_vp(
        smiles=smiles, min_temp=t_min, max_temp=t_max, npoints=npoints
    )
    exp_data = retrieve_vp_pure_data(smiles=smiles)

    plot_data = {"x": temperatures, "y": vapor_pressures}
    data = {
        "GNN": [temperatures, vapor_pressures],
        "legends": [
            "GNN",
            "GNN",
            "ThermoML Archive**",
        ],
        "TML": _experimental_plot_data(exp_data, y_scale=PA_PER_KPA),
    }
    plot_id = f"vp_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Vapor pressure (Pa) plot"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "Temperature (K)",
        "Vapor Pressure (Pa)",
        "Vapor pressure",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="vapor_pressure",
        data=plot_data,
        html=html,
        message="Vapor pressure plot generated successfully.",
    )


def plot_pure_h_lv(smiles: str, t_min: float, t_max: float, npoints: int = 100):
    """
    When asked, use this tool to show the user a plot of enthalpy of vaporization (kJ/mol).

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate enthalpy of vaporization (kJ/mol)
      t_max (float): maximun temperature (K) to calculate enthalpy of vaporization (kJ/mol)
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """

    temperatures, h_lv = pure_h_lv(
        smiles=smiles, min_temp=t_min, max_temp=t_max, npoints=npoints
    )

    plot_data = {"x": temperatures, "y": h_lv}
    data = {
        "GNN": [temperatures, h_lv],
        "legends": [
            "GNN",
            "GNN",
            "ThermoML Archive**",
        ],
        "TML": [[], []],
    }
    plot_id = f"h_lv_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Enthalpy of vaporization (kJ/mol) plot"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "Temperature (K)",
        "Enthalpy of vaporization (kJ/mol)",
        "Enthalpy of vaporization",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="enthalpy_vaporization",
        data=plot_data,
        html=html,
        message="Enthalpy of vaporization plot generated successfully.",
    )


def plot_pure_surface_tension(smiles: str, t_min: float):
    """
    When asked, use this tool to show the user a plot of Surface Tension (mN/m)
    from t_min up to the critical temperature.

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate Surface Tension (mN/m)

    """

    st, temperatures = pure_surface_tension(smiles=smiles, min_temp=t_min)
    exp_data = retrieve_st_pure_data(smiles=smiles)

    plot_data = {"x": temperatures, "y": st}
    data = {
        "GNN": [temperatures, st],
        "legends": [
            "GNN",
            "GNN",
            "ThermoML Archive**",
        ],
        "TML": _experimental_plot_data(exp_data, y_scale=MN_PER_N),
    }
    plot_id = f"st_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Surface Tension (mN/m) plot"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "Temperature (K)",
        "Surface Tension (mN/m)",
        "Surface Tension",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="surface_tension",
        data=plot_data,
        html=html,
        message="Surface tension plot generated successfully.",
    )


def plot_pure_phase_diagram_t_rho_and_p_rho(smiles: str, t_min: float):
    """
    When asked, use this tool to show the user a pure-component
    temperature (K) vs density (mol/m³) and pressure (Pa) vs density (mol/m³)
    phase diagram from t_min up to the critical temperature.

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate phase diagram

    """

    output = pure_phase_diagram(smiles=smiles, min_temp=t_min)

    plot_data = {
        "temperature": output[0],
        "pressure": output[1],
        "density_liquid": output[2],
        "density_vapor": output[3],
    }
    data_t_rho = {
        "GNN": [
            output[0],
            output[2],
            output[3],
        ],
        "legends": [
            "GNN - Liquid",
            "GNN - Vapor",
            "Exp. Bubble P. (ThermoML Archive**)",
        ],
        "TML": [[], []],
    }
    data_p_rho = {
        "GNN": [
            output[1],
            output[2],
            output[3],
        ],
        "legends": [
            "GNN - Liquid",
            "GNN - Vapor",
            "Exp. Bubble P. (ThermoML Archive**)",
        ],
        "TML": [[], []],
    }
    plot_id_t_rho = f"t_rho_diagram_{uuid.uuid4().hex}"
    plot_id_p_rho = f"p_rho_diagram_{uuid.uuid4().hex}"
    html = f"""
    <div class="mb-2" id="{plot_id_t_rho}" alt="Phase diagram plot T-rho"></div>
    <div id="{plot_id_p_rho}" alt="Phase diagram plot P-rho"></div>
    <script>
    getplot_fixed_y(
        {json.dumps(data_t_rho)},
        "Density (mol/m³)",
        "Temperature (K)",
        "Phase Diagram T-rho",
        "{plot_id_t_rho}");
    getplot_fixed_y(
        {json.dumps(data_p_rho)},
        "Density (mol/m³)",
        "Pressure (Pa)",
        "Phase Diagram P-rho",
        "{plot_id_p_rho}");
    </script>
    """
    return _make_plot_response(
        plot_type="phase_diagram",
        data=plot_data,
        html=html,
        message="Phase diagram generated successfully.",
    )
