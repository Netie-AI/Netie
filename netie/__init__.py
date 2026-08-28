"""Portable Netie contracts for product repos.

    uv add git+https://github.com/Netie-AI/Netie.git
    from netie.crew import bind_deep_agent, crew_harness_profile, TokenBudget, dispatch_seat
    from netie.cortex import run_question
    from netie.dms import answer_or_abstain, browse_or_abstain
    from netie.airgpt import retrieve_space, chunk_table
    from netie.pointer import bind_computer, invoke_hand
    from netie.space import chat_preview
    from netie.control import project_board, project_session, MAX_BOARD_CHARS
    from netie.route import host_switchyard, report_deploy, compile_graph

A wheel ships the contract modules as netie._contracts. Editable checkout still works.
Do not vendor OpenWork ee/ or Grok Bot reconstructed.
"""
