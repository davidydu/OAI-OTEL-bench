from __future__ import annotations

from Bio.PDB import PDBParser

from ..file_router import Attachment


class PDBProcessorAgent:
    """Extract a simple summary from PDB files."""

    def process(self, att: Attachment) -> str:
        parser = PDBParser(QUIET=True)
        if att.path.exists():
            with att.path.open("rb") as handle:
                structure = parser.get_structure("structure", handle)
        else:
            from io import BytesIO

            structure = parser.get_structure("structure", BytesIO(att.bytes))
        chains = []
        for model in structure:
            for chain in model:
                chains.append(
                    f"Chain {chain.id} with {len(list(chain.get_residues()))} residues"
                )
        return "\n".join(chains)
