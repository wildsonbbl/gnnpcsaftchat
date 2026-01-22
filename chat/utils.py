"Module for utils like plotting data."

import os.path as osp

import onnxruntime as ort
from rdkit.Chem import AllChem as Chem

ort.set_default_logger_severity(3)

available_params = [
    "Segment number",
    "Segment diameter (Å)",
    "Dispersion energy (K)",
    "Association volume",
    "Association energy (K)",
    "Dipole moment (D)*",
    "Number of association site A",
    "Number of association site B",
    "Molecular weight (g/mol)",
    "Critical temperature (K)",
    "Critical pressure (Bar)",
]

file_dir = osp.dirname(__file__)
dataset_dir = osp.join(file_dir, "data")


def plotmol(inchi: str) -> str:
    "Make Mol block for 3Dmol."

    mol = Chem.MolFromInchi(inchi)
    mol = Chem.AddHs(mol)  # type: ignore
    params = Chem.ETKDGv3()  # type: ignore
    params.randomSeed = 0xF00D
    result = Chem.EmbedMolecule(mol, params)  # type: ignore
    if result == 0:
        Chem.MMFFOptimizeMolecule(  # type: ignore
            mol, maxIters=1000, nonBondedThresh=100, ignoreInterfragInteractions=False
        )
    # mol = Chem.RemoveHs(mol, implicitOnly=False)
    imgmol = Chem.MolToV3KMolBlock(mol)  # type: ignore
    return imgmol
