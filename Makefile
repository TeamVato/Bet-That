.PHONY: db-ratings import-odds edges ui

db-ratings:
	python jobs/build_defense_ratings.py

import-odds:
	python jobs/import_odds_from_csv.py

edges:
	python jobs/compute_edges.py

ui:
	PYTHONPATH="$(pwd)" streamlit run app/streamlit_app.py
