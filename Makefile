# Local estate gate. Same command as .github/workflows/docs-ci.yml.
# GitHub docs-ci on main is green. This is still the merge gate this agent runs.
.PHONY: ci compile
compile:
	python3 -m compileall -q scripts netie
ci: compile
	python3 scripts/check_docs.py
