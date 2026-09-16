"""
Legal Evidence Graph Engine
"""

from typing import Any
from backend.schemas.eglr import ClauseObject, DocumentMetadata, Obligation


class LegalEvidenceGraph:
    """
    Constructs and queries an in-memory property graph representing documents,
    clauses, parties, obligations, rights, and conflict relationships.
    """

    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

    def add_document_subgraph(self, meta: DocumentMetadata, clauses: list[ClauseObject]) -> None:
        """
        Builds graph elements for a newly ingested document with tenant isolation.
        """
        tenant_id = meta.tenant_id

        # Document Node
        self.nodes[meta.document_id] = {
            "id": meta.document_id,
            "type": "Document",
            "label": meta.title,
            "filename": meta.filename,
            "version": meta.document_version,
            "jurisdiction": meta.jurisdiction,
            "tenant_id": tenant_id
        }

        # Party Nodes
        for p in meta.parties:
            party_id = f"PARTY_{p.upper().replace(' ', '_')}"
            self.nodes[party_id] = {
                "id": party_id,
                "type": "Party",
                "label": p,
                "tenant_id": tenant_id
            }
            self.edges.append({
                "source": meta.document_id,
                "target": party_id,
                "relationship": "HAS_PARTY",
                "tenant_id": tenant_id
            })

        # Clause & Obligation Nodes
        for c in clauses:
            self.nodes[c.clause_id] = {
                "id": c.clause_id,
                "type": "Clause",
                "label": c.title,
                "section": c.section,
                "page": c.page,
                "text": c.text,
                "risk_level": c.risk_level.value,
                "tenant_id": tenant_id
            }
            self.edges.append({
                "source": meta.document_id,
                "target": c.clause_id,
                "relationship": "CONTAINS_CLAUSE",
                "tenant_id": tenant_id
            })

            # Check for obligations
            for idx, ob in enumerate(c.obligations):
                ob_id = f"OB_{c.clause_id}_{idx}"
                self.nodes[ob_id] = {
                    "id": ob_id,
                    "type": "Obligation",
                    "label": f"Obligation: {ob.party}",
                    "text": ob.obligation_text,
                    "party": ob.party,
                    "deadline": ob.deadline,
                    "penalty": ob.penalty,
                    "tenant_id": tenant_id
                }
                self.edges.append({
                    "source": c.clause_id,
                    "target": ob_id,
                    "relationship": "CREATES_OBLIGATION",
                    "tenant_id": tenant_id
                })

    def detect_graph_conflicts(self, tenant_id: str = None) -> list[dict[str, Any]]:
        """
        Scans graph nodes for potential legal contradictions with optional tenant filtering.
        """
        conflicts = []
        clause_nodes = [n for n in self.nodes.values() if n["type"] == "Clause" and (tenant_id is None or n.get("tenant_id") == tenant_id)]
        notice_clauses = [c for c in clause_nodes if "notice" in c["label"].lower()]

        for i in range(len(notice_clauses)):
            for j in range(i + 1, len(notice_clauses)):
                c1 = notice_clauses[i]
                c2 = notice_clauses[j]
                if c1["text"] != c2["text"]:
                    conflicts.append({
                        "clause_a": c1["id"],
                        "clause_b": c2["id"],
                        "type": "NOTICE_PERIOD_MISMATCH",
                        "description": f"Conflicting notice requirements between {c1['label']} and {c2['label']}"
                    })
        return conflicts

    def get_exportable_graph(self, tenant_id: str = None) -> dict[str, Any]:
        """
        Returns JSON representation of nodes and edges filtered by tenant_id.
        """
        if tenant_id:
            filtered_nodes = [n for n in self.nodes.values() if n.get("tenant_id") == tenant_id]
            filtered_edges = [e for e in self.edges if e.get("tenant_id") == tenant_id]
            return {
                "nodes": filtered_nodes,
                "edges": filtered_edges
            }

        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges
        }
