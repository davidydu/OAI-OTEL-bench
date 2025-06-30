from __future__ import annotations

from Bio.PDB import PDBParser

from ..file_router import Attachment


class PDBProcessorAgent:
    """Extract a simple summary from PDB files."""

    def process(self, att: Attachment) -> str:
        parser = PDBParser(QUIET=True)
        with att.path.open("rb") as handle:
            structure = parser.get_structure("structure", handle)
        chains = []
        for model in structure:
            for chain in model:
                chains.append(
                    f"Chain {chain.id} with {len(list(chain.get_residues()))} residues"
                )
        return "\n".join(chains)
