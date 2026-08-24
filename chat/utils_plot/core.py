"core helper for plotting"

import uuid
from typing import Any, Dict, List, Optional

import numpy as np
from gnnepcsaft_mcp_server.plot_utils import v3000_mol_block

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
