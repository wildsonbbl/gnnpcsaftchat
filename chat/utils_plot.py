"helper for plotting"

import json
import uuid
from typing import Any, Dict, List, Optional

import numpy as np
from gnnepcsaft_mcp_server.plot_utils import v3000_mol_block
from gnnepcsaft_mcp_server.utils_data import (
    retrieve_bubble_pressure_data,
    retrieve_lle_binary_data,
    retrieve_lle_ternary_data,
    retrieve_rho_binary_data,
    retrieve_rho_pure_data,
    retrieve_rho_ternary_data,
    retrieve_st_pure_data,
    retrieve_vle_binary_data,
    retrieve_vle_pxy_binary_data,
    retrieve_vle_ternary_data,
    retrieve_vle_ternary_tx_fixed_data,
    retrieve_vp_pure_data,
)
from gnnepcsaft_mcp_server.utils_mix import (
    MixDenParams,
    MixLLEParams,
    MixVpParams,
    TernaryVleTxParams,
    mix_den,
    mix_lle,
    mix_ternary_lle,
    mix_ternary_vle_tx_fixed,
    mix_vle,
    mix_vle_pxy,
    mix_vp,
)
from gnnepcsaft_mcp_server.utils_pure import (
    pure_den,
    pure_h_lv,
    pure_phase_diagram,
    pure_surface_tension,
    pure_vp,
)

PLOT_HTML_STORE: Dict[str, str] = {}
PA_PER_KPA = 1000.0
MN_PER_N = 1000.0


def _experimental_plot_data(
    data: Optional[np.ndarray], x_scale: float = 1.0, y_scale: float = 1.0
) -> List[List[float]]:
    """Convert experimental rows into the frontend's ``[x, y]`` format."""
    if data is None or data.size == 0:
        return [[], []]
    converted = data.astype(np.float64, copy=True)
    converted[:, 0] *= x_scale
    converted[:, 1] *= y_scale
    return converted.T.tolist()


def _make_plot_response(
    plot_type: str,
    data: Dict[str, Any],
    html: str,
    success: bool = True,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a compact tool response for the agent and keep HTML for frontend use."""
    plot_id = f"{plot_type}_{uuid.uuid4().hex}"
    PLOT_HTML_STORE[plot_id] = html
    return {
        "success": success,
        "message": message
        or ("Plot rendered successfully." if success else "Plot failed to render."),
        "plot_id": plot_id,
        "plot_type": plot_type,
        "data": data,
    }


def pop_plot_html(plot_id: str) -> Optional[str]:
    """Retrieve and remove a stored plot HTML block for client rendering."""
    return PLOT_HTML_STORE.pop(plot_id, None)


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

    plot_data = {"x": temperatures, "y": densities}
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


def plot_mix_density(  # pylint: disable=R0913,R0917
    smiles_list: List[str],
    t_min: float,
    t_max: float,
    pressure: float,
    mole_fractions: List[float],
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a plot of density (mol/m³) for a mixture.

    Args:
      smiles_list (List[str]): List of mixture SMILES.
      t_min (float): minimum temperature (K) to calculate density (mol/m³)
      t_max (float): maximun temperature (K) to calculate density (mol/m³)
      pressure (float): system pressure (Pa)
      mole_fractions (List[float]): mole fractions list
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """

    temperatures, densities = mix_den(
        MixDenParams(
            smiles_list=smiles_list,
            mole_fractions=mole_fractions,
            kij_matrix=kij_matrix if kij_matrix else [],
            min_temp=t_min,
            max_temp=t_max,
            pressure=pressure,
            npoints=npoints,
        )
    )

    if len(smiles_list) == 2:
        exp_data = retrieve_rho_binary_data(
            smiles_list=smiles_list,
            pressure=pressure / PA_PER_KPA,
            x1=mole_fractions[0],
        )
    elif len(smiles_list) == 3:
        exp_data = retrieve_rho_ternary_data(
            smiles_list=smiles_list,
            pressure=pressure / PA_PER_KPA,
            x1=mole_fractions[0],
            x2=mole_fractions[1],
        )
    else:
        exp_data = None

    plot_data = {"x": temperatures, "y": densities}
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
        "Density plot (mol/m³)",
        "Density at P={pressure} Pa and mole fractions={mole_fractions}",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="mixture_density",
        data=plot_data,
        html=html,
        message="Mixture density plot generated successfully.",
    )


def plot_mix_vle_pt(
    smiles_list: List[str],
    t_min: float,
    t_max: float,
    mole_fractions: List[float],
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a plot of Bubble/Dew points (Pa) for a mixture
    with any number of components.

    Args:
      smiles_list (List[str]): List of mixture SMILES [SMILES_1, SMILES_2, SMILES_3, ...].
      t_min (float): minimum temperature (K) to calculate Bubble/Dew points (Pa)
      t_max (float): maximun temperature (K) to calculate Bubble/Dew points (Pa)
      mole_fractions (List[float]): mole fractions list [X1, X2, X3, ...]
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """

    temperatures, bubble, dew = mix_vp(
        MixVpParams(
            smiles_list=smiles_list,
            mole_fractions=mole_fractions,
            kij_matrix=kij_matrix if kij_matrix else [],
            min_temp=t_min,
            max_temp=t_max,
            npoints=npoints,
        )
    )

    exp_data = (
        retrieve_bubble_pressure_data(smiles_list, mole_fractions[0])
        if len(smiles_list) == 2
        else None
    )

    plot_data = {"x": temperatures, "bubble": bubble, "dew": dew}
    data = {
        "GNN": [temperatures, bubble, dew],
        "legends": [
            "GNN Bubble P.",
            "GNN Dew P.",
            "Exp. Bubble P. (ThermoML Archive**)",
        ],
        "TML": _experimental_plot_data(exp_data, y_scale=PA_PER_KPA),
    }
    plot_id = f"bubble_dew_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Bubble/Dew points (Pa)"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "Temperature (K)",
        "Pressure (Pa)",
        "VLE at mole fractions={mole_fractions}",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="bubble_dew",
        data=plot_data,
        html=html,
        message="Bubble/dew plot generated successfully.",
    )


def plot_binary_lle_txx(
    smiles_list: List[str],
    temp_min_and_max: List[float],
    pressure: float,
    mole_fractions: List[float],
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a T-x-x LLE diagram for a binary mixture
    from t_min to t_max K at pressure (Pa). Mole fractions are used as starting value,
    so it needs to be within the two phase region.

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      temp_min_and_max (List[float]): Temperature min and max (K) [t_min, t_max]
        to calculate LLE diagram within
      pressure (float): System pressure (Pa)
      mole_fractions (List[float]): Global mole fractions [x1, x2] used as starting value
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    output = mix_lle(
        MixLLEParams(
            smiles_list=smiles_list,
            mole_fractions=mole_fractions,
            kij_matrix=kij_matrix if kij_matrix else [],
            temperature_min=min(temp_min_and_max),
            temperature_max=max(temp_min_and_max),
            pressure=pressure,
            npoints=npoints,
        )
    )

    if output is None:
        return "Failed to calculate LLE T-x-x for these conditions"

    plot_data = {
        "temperature": output["temperature"],
        "x0": output["x0"],
        "y0": output["y0"],
    }
    data = {
        "GNN": [
            output["temperature"],
            output["x0"],
            output["y0"],
        ],
        "legends": ["GNN - Phase 1", "GNN - Phase 2", "ThermoML Archive**"],
        "TML": _experimental_plot_data(
            retrieve_lle_binary_data(smiles_list, pressure / PA_PER_KPA)
        ),
    }
    plot_id = f"b_lle_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Binary LLE diagram"></div>
    <script>
    getplot_fixed_y(
        {json.dumps(data)},
        "x<sub>1</sub>",
        "Temperature (K)",
        "LLE at P={pressure} Pa",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="binary_lle",
        data=plot_data,
        html=html,
        message="Binary LLE diagram generated successfully.",
    )


def plot_binary_vle_txy(
    smiles_list: List[str],
    pressure: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a T-x-y VLE diagram for a binary mixture
    at pressure (Pa).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    output = mix_vle(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [],
        pressure=pressure,
        npoints=npoints,
    )

    if output is None:
        return "Failed to calculate VLE T-x-y for these conditions"

    plot_data = {
        "temperature": output["temperature"],
        "x0": output["x0"],
        "y0": output["y0"],
    }
    data = {
        "GNN": [
            output["temperature"],
            output["x0"],
            output["y0"],
        ],
        "legends": ["GNN - Phase 1", "GNN - Phase 2", "ThermoML Archive**"],
        "TML": _experimental_plot_data(
            retrieve_vle_binary_data(smiles_list, pressure / PA_PER_KPA)
        ),
    }
    plot_id = f"b_vle_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Binary VLE diagram"></div>
    <script>
    getplot_fixed_y(
        {json.dumps(data)},
        "x<sub>1</sub>, y<sub>1</sub>",
        "Temperature (K)",
        "VLE at P={pressure} Pa",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="binary_vle",
        data=plot_data,
        html=html,
        message="Binary VLE diagram generated successfully.",
    )


def plot_binary_vle_xy(
    smiles_list: List[str],
    pressure: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a x-y VLE diagram for a binary mixture
    at pressure (Pa).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    output = mix_vle(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [],
        pressure=pressure,
        npoints=npoints,
    )

    if output is None:
        return "Failed to calculate VLE x-y for these conditions"

    plot_data = {"x0": output["x0"], "y0": output["y0"]}
    data = {
        "GNN": [
            output["x0"],
            output["y0"],
        ],
        "legends": ["GNN", "GNN", "ThermoML Archive**"],
        "TML": [[], []],
    }
    plot_id = f"b_vle_xy_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Binary VLE diagram"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "x<sub>1</sub>",
        "y<sub>1</sub>",
        "VLE at P={pressure} Pa",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="binary_vle_xy",
        data=plot_data,
        html=html,
        message="Binary x-y VLE diagram generated successfully.",
    )


def plot_binary_vle_pxy(
    smiles_list: List[str],
    temperature: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a P-x-y VLE diagram for a binary mixture
    at Temperature (K).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      temperature (float): System Temperature (K)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    xs, bps, dps = mix_vle_pxy(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [],
        temperature=temperature,
        npoints=npoints,
    )

    plot_data = {
        "bubble_points": bps,
        "dew_points": dps,
        "x1s": xs,
    }
    data = {
        "GNN": [
            xs,
            bps,
            dps,
        ],
        "legends": [
            "GNN Bubble P.",
            "GNN Dew P.",
            "Exp. Bubble P. (ThermoML Archive**)",
        ],
        "TML": _experimental_plot_data(
            retrieve_vle_pxy_binary_data(smiles_list, temperature), y_scale=PA_PER_KPA
        ),
    }
    plot_id = f"b_vle_pxy_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Binary VLE P-x-y diagram"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "x<sub>1</sub>, y<sub>1</sub>",
        "Pressure (Pa)",
        "VLE at T={temperature} K",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="binary_vle_pxy",
        data=plot_data,
        html=html,
        message="Binary VLE P-x-y diagram generated successfully.",
    )


def plot_ternary_vle_pxy(
    smiles_list: List[str],
    temperature: float,
    solvent_ratio: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a P-x-y VLE diagram for a ternary mixture
    at fixed Temperature (K) and solvent ratio.

    Solvent_ratio = x2 / (x2 + x3). The first component is scanned in composition.

    Args:
      smiles_list (List[str]): List with ternary SMILES [SMILES_1, SMILES_2, SMILES_3].
      temperature (float): System Temperature (K).
      solvent_ratio (float): Solvent_ratio = x2 / (x2 + x3).
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 3
    ), f"smiles_list should have 3 SMILES, got {len(smiles_list)} instead"

    xs, bps, dps = mix_ternary_vle_tx_fixed(
        TernaryVleTxParams(
            smiles_list=smiles_list,
            kij_matrix=kij_matrix if kij_matrix else [],
            temperature=temperature,
            solvent_ratio=solvent_ratio,
            npoints=npoints,
        )
    )

    plot_data = {
        "bubble_points": bps,
        "dew_points": dps,
        "x1s": xs,
    }
    data = {
        "GNN": [
            xs,
            bps,
            dps,
        ],
        "legends": [
            "GNN Bubble P.",
            "GNN Dew P.",
            "Exp. Bubble P. (ThermoML Archive**)",
        ],
        "TML": _experimental_plot_data(
            retrieve_vle_ternary_tx_fixed_data(smiles_list, temperature, solvent_ratio),
            y_scale=PA_PER_KPA,
        ),
    }
    plot_id = f"t_vle_pxy_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Ternary VLE P-x-y diagram"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "x<sub>1</sub>, y<sub>1</sub>",
        "Pressure (Pa)",
        "VLE at T={temperature} K and x2/(x2+x3)={solvent_ratio}",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="ternary_vle_pxy",
        data=plot_data,
        html=html,
        message="Ternary VLE P-x-y diagram generated successfully.",
    )


def plot_ternary_lle_or_vle(
    smiles_list: List[str],
    temperature: float,
    pressure: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 25,
):
    """
    When asked, use this tool to show the user a LLE or VLE diagram for a ternary mixture
    at temperature (K) and pressure (Pa).

    Args:
      smiles_list (List[str]): List with ternary SMILES [SMILES_1, SMILES_2, SMILES_3].
      temperature (float): System temperature (K)
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 25 data points.

    """
    assert (
        len(smiles_list) == 3
    ), f"smiles_list should have 3 SMILES, got {len(smiles_list)} instead"

    output = mix_ternary_lle(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [],
        temperature=temperature,
        pressure=pressure,
        npoints=npoints,
    )
    experimental_rows = [
        data
        for data in (
            retrieve_lle_ternary_data(smiles_list, pressure / PA_PER_KPA, temperature),
            retrieve_vle_ternary_data(smiles_list, pressure / PA_PER_KPA, temperature),
        )
        if data is not None and data.size > 0
    ]
    if experimental_rows:
        experimental_data = np.vstack(experimental_rows)
        output.update(
            {
                "exp_x0": experimental_data[:, 0].tolist(),
                "exp_x1": experimental_data[:, 1].tolist(),
                "exp_x2": (
                    1.0 - experimental_data[:, 0] - experimental_data[:, 1]
                ).tolist(),
            }
        )
    else:
        output.update({"exp_x0": [], "exp_x1": [], "exp_x2": []})
    plot_data = output
    plot_id = f"t_lle_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Ternary LLE/VLE diagram"></div>
    <script>
    get_ternary_lle_phase_diagram(
        {json.dumps(output)},
        {temperature},
        {pressure},
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="ternary_lle_or_vle",
        data=plot_data,
        html=html,
        message="Ternary LLE/VLE diagram generated successfully.",
    )


def plot_3d_molecule(smiles: str):
    """
    When asked, use this tool to show the user a 3D molecule.

    Args:
      smiles (str): SMILES of the molecule.

    """

    mol = v3000_mol_block(smiles=smiles).replace("\n", "\\n")
    plot_id = f"3d_mol_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="3D molecule" class="molplot-style"></div>
    <script>
    var mol = "{mol}";
    loadmol(mol, "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="molecule_3d",
        data={"smiles": smiles},
        html=html,
        message="3D molecule view generated successfully.",
    )
