from __future__ import annotations


def test_strict_hypergraph_gap_is_kept_visible(matter_result):
    result = matter_result["hypergraph_robustness"]
    assert result["declared_root"] == "N036"
    assert result["baseline_nodes"] == 53
    assert result["baseline_reachable"] == 46
    assert result["baseline_unreachable"] == [
        "N029", "N030", "N031", "N032", "N035", "N053", "N054"
    ]
    gap = result["strict_gap_diagnostics"]
    assert gap["cycle_kernel_nodes"] == ["N029", "N030", "N053", "N054"]
    assert gap["downstream_nodes_blocked_by_cycle"] == ["N031", "N032", "N035"]
    assert gap["minimum_additional_seed_count"] == 1
    assert gap["single_nodes_that_restore_full_closure"] == [
        "N029", "N030", "N053", "N054"
    ]


def test_all_single_edge_deletions_are_evaluated(matter_result):
    result = matter_result["hypergraph_robustness"]
    assert result["single_edge_deletions"] == 53
    assert result["critical_edges"] == 34
    assert 0 < result["critical_edge_fraction"] < 1


def test_upstream_edge_has_large_downstream_impact(matter_result):
    top = matter_result["hypergraph_robustness"]["top_edge_impacts"][0]
    assert top["edge_id"] == "H035"
    assert top["nodes_lost"] == 45


def test_partition_conclusions_are_distinguished(matter_result):
    per_element = matter_result["partition_coefficient_robustness"]["per_element"]
    assert per_element["C"]["baseline_overlap"] is True
    assert per_element["C"]["leave_one_out_overlap_fraction"] == 1.0
    assert per_element["N"]["baseline_overlap_fragile"] is True
    assert per_element["S"]["baseline_overlap"] is False
    assert per_element["H"]["leave_one_out_overlap_fraction"] is None


def test_transition_database_keeps_missing_fields_visible(matter_result):
    result = matter_result["transition_database_completeness"]
    assert result["transitions"] == 40
    assert len(result["empty_fields"]) == 10
    assert "preuves_directes" in result["empty_fields"]
    assert "mecanismes_de_persistance" in result["empty_fields"]
