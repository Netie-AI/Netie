# Local estate gate. Same command as .github/workflows/docs-ci.yml.
# GitHub docs-ci on main is green. This is still the merge gate this agent runs.
.PHONY: ci compile drift
compile:
	python3 -m compileall -q scripts netie
ci: compile
	python3 scripts/check_docs.py
# Network: re-hash every upstream license. Not part of ci, so an upstream outage cannot block a merge.
drift:
	python3 scripts/ecosystem.py drift
