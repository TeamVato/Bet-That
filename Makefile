SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c

DRY ?= 0
MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))

# run <command>
# If DRY=1, only print the command. Otherwise execute it with eval for shell features.
define run
	@cmd='$(1)'; \
	if [ "$(DRY)" = "1" ]; then \
		printf '[DRY] %s\n' "$$cmd"; \
	else \
		printf '+ %s\n' "$$cmd"; \
		eval "$$cmd"; \
	fi
endef

.PHONY: repo-fresh repo-clean repo-status audit-quarantine pr-fix-dirty-tripwire protect readme solo-merge pr-list open-pr pr-status help betthat db-ratings import-odds edges ui lint-streamlit

help: ## Show available make targets
	@printf "Available targets (set DRY=1 to preview):\n"
	@awk 'BEGIN {FS = ":.*##"} /^[A-Za-z0-9_.-]+:.*##/ { printf "  %-30s %s\n", $$1, $$2 }' "$(MAKEFILE_PATH)"

repo-status: ## Summarize git status
	$(call run,git status -sb)

repo-clean: ## Remove untracked files (keeps .venv)
	$(call run,git clean -xfd -e .venv)

repo-fresh: ## Install project dependencies
	$(call run,python -m pip install -r requirements.txt)

audit-quarantine: ## Audit quarantined paths for unexpected files
	$(call run,"./scripts/audit-quarantine.sh")

pr-fix-dirty-tripwire: ## Guard against dirty working tree on PRs
	$(call run,"./scripts/pr-fix-dirty-tripwire.sh")

protect: ## Placeholder target for branch protection workflows
	$(call run,printf 'Refer to docs/protect.md for details\n')

readme: ## Point to repository README guidance
	$(call run,printf 'README lives at README.md\n')

solo-merge: ## Document solo merge flow
	$(call run,printf 'See docs/solo-merge.md for guidance\n')

pr-list: ## List open PRs (placeholder)
	$(call run,printf 'Use gh pr list to list GitHub PRs\n')

open-pr: ## Open a new PR in browser (placeholder)
	$(call run,printf 'Use gh pr create --web to open a PR\n')

pr-status: ## Show PR status summary (placeholder)
	$(call run,printf 'Use gh pr status for pull request status\n')

betthat: ## Run the full local pipeline and launch the UI
        $(call run,./scripts/betthat.sh)

db-ratings: ## Build defense ratings dataset
        $(call run,. .venv/bin/activate && python jobs/build_defense_ratings.py)

import-odds: ## Import odds data from CSV
        $(call run,. .venv/bin/activate && python jobs/import_odds_from_csv.py)

edges: ## Compute betting edges
        $(call run,. .venv/bin/activate && python jobs/compute_edges.py)

ui: ## Launch Streamlit UI
	$(call run,PYTHONPATH="$(CURDIR)" . .venv/bin/activate && streamlit run app/streamlit_app.py)

lint-streamlit: ## Ensure Streamlit deprecated arguments are not used
	$(call run,./scripts/lint_streamlit.sh)
