# Local estate gate. Same as .github/workflows/docs-ci.yml once billing works.
.PHONY: ci
ci:
	python3 scripts/check_docs.py
