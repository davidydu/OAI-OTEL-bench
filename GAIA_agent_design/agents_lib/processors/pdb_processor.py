from __future__ import annotations

from io import BytesIO
from Bio.PDB import PDBParser


class PDBProcessorAgent:
    """Extract a simple summary from PDB files."""

    def process(self, raw: bytes, mime_type: str) -> str:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("structure", BytesIO(raw))
        chains = []
        for model in structure:
            for chain in model:
                chains.append(
                    f"Chain {chain.id} with {len(list(chain.get_residues()))} residues"
                )
        return "\n".join(chains)
