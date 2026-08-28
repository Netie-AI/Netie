# Local estate gate. Same command as .github/workflows/docs-ci.yml.
# GitHub governed-docs never starts (org spending limit). This is the merge gate.
.PHONY: ci compile
compile:
	python3 -m compileall -q scripts netie
ci: compile
	python3 scripts/check_docs.py
