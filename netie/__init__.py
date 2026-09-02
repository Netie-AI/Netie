"""Portable Netie contracts for product repos.

    uv add git+https://github.com/Netie-AI/Netie.git
    from netie.crew import bind_deep_agent, crew_harness_profile, TokenBudget, dispatch_seat, persist, resume, register_skill, register_from_kb, register_index, mint_issue
    from netie.cortex import run_question
    from netie.dms import answer_or_abstain, browse_or_abstain, mint_object
    from netie.airgpt import retrieve_space, chunk_table
    from netie.pointer import bind_computer, bind_pointer_skill, invoke_hand, guard_observe
    from netie.kb import show_brief, lookup, list_briefs
    from netie.space import chat_preview
    from netie.control import project_board, project_session, MAX_BOARD_CHARS, board_index
    from netie.route import host_switchyard, report_deploy, compile_graph, compile_ir, assist_free_pool, remember
    from netie.crew import refuse_crew_gate

A wheel ships the contract modules as netie._contracts. Editable checkout still works.
Do not vendor OpenWork ee/ or Grok Bot reconstructed.
"""
