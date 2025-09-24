# Simple EDA script for QB projection calibration
suppressPackageStartupMessages({
  library(DBI)
  library(RSQLite)
  library(dplyr)
  library(readr)
  library(ggplot2)
})

args <- commandArgs(trailingOnly = FALSE)
script_path <- sub('--file=', '', args[grep('--file=', args)])
if (length(script_path) == 0) {
  script_dir <- getwd()
} else {
  script_dir <- dirname(script_path)
}
repo_root <- normalizePath(file.path(script_dir, '..'), winslash = '/', mustWork = FALSE)
db_path <- file.path(repo_root, 'storage', 'odds.db')
if (!file.exists(db_path)) {
  stop('SQLite database not found at ', db_path, '. Run the Python jobs first.')
}

con <- dbConnect(RSQLite::SQLite(), db_path)
on.exit(dbDisconnect(con))

props <- dbReadTable(con, 'qb_props_odds')
projections <- dbReadTable(con, 'projections_qb')
edges <- dbReadTable(con, 'edges')

merged <- props %>%
  inner_join(projections, by = c('event_id', 'player'), suffix = c('_props', '_proj')) %>%
  mutate(
    residual = mu - line,
    model_edge = ev_per_dollar
  )

if (nrow(merged) == 0) {
  message('No data to analyze yet. Run jobs/compute_edges.py first.')
} else {
  summary_tbl <- merged %>%
    group_by(player) %>%
    summarise(
      games = n(),
      avg_residual = mean(residual, na.rm = TRUE),
      sd_residual = sd(residual, na.rm = TRUE)
    ) %>%
    arrange(desc(games))

  export_dir <- file.path(repo_root, 'r', 'exports')
  dir.create(export_dir, recursive = TRUE, showWarnings = FALSE)
  write_csv(summary_tbl, file.path(export_dir, 'eda_summary.csv'))

  ggplot(merged, aes(x = residual)) +
    geom_histogram(binwidth = 10, fill = 'steelblue', alpha = 0.7) +
    labs(title = 'QB Projection Residuals', x = 'Model - Line (yards)', y = 'Count')
}
