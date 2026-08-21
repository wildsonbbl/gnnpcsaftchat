"helper for plotting"

import json
import uuid
from typing import Any, Dict, List, Optional

import numpy as np
from gnnepcsaft.pcsaft.pcsaft_feos import (
    mix_den_feos,
    mix_lle_diagram_feos,
    mix_lle_feos,
    mix_vle_diagram_feos,
    mix_vp_feos,
    phase_diagram_feos,
    pure_den_feos,
    pure_h_lv_feos,
    pure_surface_tension_feos,
    pure_vp_feos,
)
from gnnepcsaft_mcp_server.plot_utils import v3000_mol_block
from gnnepcsaft_mcp_server.utils import predict_pcsaft_parameters

from .utils_data import (
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
    retrieve_vp_pure_data,
)
from .utils_mix import mix_vle_pxy

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


def plot_pure_density(smiles: str, t_min: float, t_max: float, pressure: float):
    """
    When asked, use this tool to show the user a plot of density (mol/m³).

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate density (mol/m³)
      t_max (float): maximun temperature (K) to calculate density (mol/m³)
      pressure (float): system pressure (Pa)

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = predict_pcsaft_parameters(smiles)

    densities = [
        pure_den_feos(parameters=parameters, state=[T, pressure]) for T in temperatures
    ]
    exp_data = retrieve_rho_pure_data(smiles=smiles, pressure=pressure / PA_PER_KPA)

    plot_data = {"x": temperatures.tolist(), "y": densities}
    data = {
        "GNN": [temperatures.tolist(), densities],
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


def plot_pure_vapor_pressure(smiles: str, t_min: float, t_max: float):
    """
    When asked, use this tool to show the user a plot of vapor pressure (Pa).

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate vapor pressure (Pa)
      t_max (float): maximun temperature (K) to calculate vapor pressure (Pa)

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = predict_pcsaft_parameters(smiles)

    vapor_pressures = [
        pure_vp_feos(parameters=parameters, state=[T]) for T in temperatures
    ]
    exp_data = retrieve_vp_pure_data(smiles=smiles)

    plot_data = {"x": temperatures.tolist(), "y": vapor_pressures}
    data = {
        "GNN": [temperatures.tolist(), vapor_pressures],
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


def plot_pure_h_lv(smiles: str, t_min: float, t_max: float):
    """
    When asked, use this tool to show the user a plot of enthalpy of vaporization (kJ/mol).

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate enthalpy of vaporization (kJ/mol)
      t_max (float): maximun temperature (K) to calculate enthalpy of vaporization (kJ/mol)

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = predict_pcsaft_parameters(smiles)

    h_lv = [pure_h_lv_feos(parameters=parameters, state=[T]) for T in temperatures]

    plot_data = {"x": temperatures.tolist(), "y": h_lv}
    data = {
        "GNN": [temperatures.tolist(), h_lv],
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

    parameters = predict_pcsaft_parameters(smiles)

    st, temperatures = pure_surface_tension_feos(parameters=parameters, state=[t_min])
    exp_data = retrieve_st_pure_data(smiles=smiles)

    plot_data = {"x": temperatures.tolist(), "y": st.tolist()}
    data = {
        "GNN": [temperatures.tolist(), st.tolist()],
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

    parameters = predict_pcsaft_parameters(smiles)

    output = phase_diagram_feos(parameters=parameters, state=[t_min])

    plot_data = {
        "temperature": output["temperature"],
        "pressure": output.get("pressure", output.get("pressure vapor", [])),
        "density_liquid": output["density liquid"],
        "density_vapor": output["density vapor"],
    }
    data_t_rho = {
        "GNN": [
            output["temperature"],
            output["density liquid"],
            output["density vapor"],
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
            output.get("pressure", output.get("pressure vapor", [])),
            output["density liquid"],
            output["density vapor"],
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

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = [predict_pcsaft_parameters(smiles) for smiles in smiles_list]

    densities = [
        mix_den_feos(
            parameters=parameters,
            state=[T, pressure, *mole_fractions],
            kij_matrix=kij_matrix,
        )
        for T in temperatures
    ]

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

    plot_data = {"x": temperatures.tolist(), "y": densities}
    data = {
        "GNN": [temperatures.tolist(), densities],
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

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = [predict_pcsaft_parameters(smiles) for smiles in smiles_list]

    results = [
        mix_vp_feos(
            parameters=parameters,
            state=[T, 0.0, *mole_fractions],
            kij_matrix=kij_matrix,
        )
        for T in temperatures
    ]
    bubble, dew = [list(x) for x in zip(*results)]

    exp_data = (
        retrieve_bubble_pressure_data(smiles_list, mole_fractions[0])
        if len(smiles_list) == 2
        else None
    )

    plot_data = {"x": temperatures.tolist(), "bubble": bubble, "dew": dew}
    data = {
        "GNN": [temperatures.tolist(), bubble, dew],
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

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    parameters = [predict_pcsaft_parameters(smiles) for smiles in smiles_list]

    output = mix_lle_diagram_feos(
        parameters=parameters,
        state=[
            *temp_min_and_max,
            pressure,
            *mole_fractions,
        ],
        kij_matrix=kij_matrix,
    )

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
):
    """
    When asked, use this tool to show the user a T-x-y VLE diagram for a binary mixture
    at pressure (Pa).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    parameters = [predict_pcsaft_parameters(smiles) for smiles in smiles_list]

    output = mix_vle_diagram_feos(
        parameters=parameters,
        state=[pressure],
        kij_matrix=kij_matrix,
    )

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
):
    """
    When asked, use this tool to show the user a x-y VLE diagram for a binary mixture
    at pressure (Pa).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    parameters = [predict_pcsaft_parameters(smiles) for smiles in smiles_list]

    output = mix_vle_diagram_feos(
        parameters=parameters,
        state=[pressure],
        kij_matrix=kij_matrix,
    )

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
):
    """
    When asked, use this tool to show the user a P-x-y VLE diagram for a binary mixture
    at Temperature (K).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      temperature (float): System Temperature (K)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    xs, bps, dps = mix_vle_pxy(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [[0.0, 0.0], [0.0, 0.0]],
        temperature=temperature,
        npoints=500,
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


def _get_ternary_lle_data(
    params: List[List[float]],
    state: List[float],
    kij_matrix: Optional[List[List[float]]] = None,
) -> Dict[str, List[float]]:
    t, p = state  # Temperatura (K) e pressão (Pa)

    def _grid(n_pts: int = 25):
        xi = np.linspace(1e-5, 0.999, n_pts, dtype=np.float64)
        x1_m, x2_m = np.meshgrid(xi, xi, indexing="xy")
        x3_m = 1.0 - x1_m - x2_m
        return x1_m, x2_m, x3_m, (x3_m >= 0.0)

    def _collect_tie_lines(x1_m, x2_m, x3_m, mask):
        valid_idx = np.argwhere(mask)
        ternary_data = {"x0": [], "x1": [], "x2": [], "y0": [], "y1": [], "y2": []}
        for i, j in valid_idx:
            try:
                lle = mix_lle_feos(
                    params,
                    [t, p, x1_m[i, j].item(), x2_m[i, j].item(), x3_m[i, j].item()],
                    kij_matrix,
                )
            except (RuntimeError, ValueError):
                continue
            # For LLE, y is one phase and x is the other phase
            ternary_data["x0"].extend(lle["x0"])
            ternary_data["x1"].extend(lle["x1"])
            ternary_data["x2"].extend(lle["x2"])
            ternary_data["y0"].extend(lle["y0"])
            ternary_data["y1"].extend(lle["y1"])
            ternary_data["y2"].extend(lle["y2"])
        return ternary_data

    x1, x2, x3, mask = _grid()
    return _collect_tie_lines(x1, x2, x3, mask)


def plot_ternary_lle_or_vle(
    smiles_list: List[str],
    temperature: float,
    pressure: float,
    kij_matrix: Optional[List[List[float]]] = None,
):
    """
    When asked, use this tool to show the user a LLE or VLE diagram for a ternary mixture
    at temperature (K) and pressure (Pa).

    Args:
      smiles_list (List[str]): List with ternary SMILES [SMILES_1, SMILES_2, SMILES_3].
      temperature (float): System temperature (K)
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.

    """
    assert (
        len(smiles_list) == 3
    ), f"smiles_list should have 3 SMILES, got {len(smiles_list)} instead"

    parameters = [predict_pcsaft_parameters(smiles) for smiles in smiles_list]

    output = _get_ternary_lle_data(
        params=parameters,
        state=[temperature, pressure],
        kij_matrix=kij_matrix,
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
