source("R/theme.R")

conc <- read_csv(file.path(data_dir, "airport_concentration_as_reported.csv"), show_col_types = FALSE) |>
  filter(enplanements >= 500000)

levels_dom <- c("Competitive (largest airline under 40%)",
                "Mixed (largest airline 40-60%)",
                "Dominated (largest airline over 60%)")

plot_data <- conc |>
  mutate(level = case_when(top_share < 0.4 ~ levels_dom[1],
                           top_share < 0.6 ~ levels_dom[2],
                           TRUE ~ levels_dom[3]),
         level = factor(level, levels = rev(levels_dom))) |>
  count(year, level) |>
  group_by(year) |>
  mutate(share = n / sum(n), total = sum(n)) |>
  arrange(year, desc(level)) |>
  group_by(year) |>
  mutate(top = cumsum(share), mid = top - share / 2) |>
  ungroup() |>
  mutate(year_label = paste0(year, "\n(", total, " airports)"),
         year_label = factor(year_label, levels = unique(year_label[order(year)])))

fills <- c("Competitive (largest airline under 40%)" = pal$conc_low,
           "Mixed (largest airline 40-60%)" = pal$conc_mid,
           "Dominated (largest airline over 60%)" = pal$conc_high)

p <- ggplot(plot_data, aes(year_label, share, fill = level)) +
  geom_col(width = 0.8, colour = pal$bg, linewidth = 0.6) +
  geom_text(
  aes(
    y = mid,
    label = percent(share, accuracy = 1),
    colour = if_else(level == levels_dom[1], pal$ink, "white")
  ),
  size = 3.6,
  fontface = "bold"
) +
  scale_fill_manual(values = fills, breaks = levels_dom, name = NULL) +
  scale_colour_identity() +
  scale_y_continuous(labels = percent, expand = expansion(mult = c(0, 0.01))) +
  labs(
    title = "Competitive airports became rarer after the mergers, then mostly recovered",
    subtitle = "Share of U.S. airports with at least 500,000 boardings a year, by how much of the traffic the largest airline carries",
    x = NULL, y = "Share of airports",
    caption = paste0(source_line, "\nAirlines are counted separately until they merged. Sample years shown.")
  ) +
  theme_story() +
  theme(panel.grid.major.x = element_blank(), legend.text = element_text(size = 10.5))

ggsave("figures/02_airport_dominance.png", p, width = 10.5, height = 6.2, dpi = 200)