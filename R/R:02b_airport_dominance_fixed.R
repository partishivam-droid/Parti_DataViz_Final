source("R/theme.R")

conc <- read_csv(file.path(data_dir, "airport_concentration_as_reported.csv"), show_col_types = FALSE)

fixed_airports <- conc |>
  filter(year == min(year), enplanements >= 500000) |>
  pull(airport)

competitive_share <- function(d) {
  d |>
    group_by(year) |>
    summarise(share = mean(top_share < 0.4), n = n(), .groups = "drop")
}

plot_data <- bind_rows(
  conc |> filter(enplanements >= 500000) |> competitive_share() |>
    mutate(sample = "All airports over 500,000 boardings in each year"),
  conc |> filter(airport %in% fixed_airports) |> competitive_share() |>
    mutate(sample = paste0("Same ", length(fixed_airports), " airports in every year"))
)

sample_levels <- c(paste0("Same ", length(fixed_airports), " airports in every year"),
                   "All airports over 500,000 boardings in each year")
plot_data <- plot_data |> mutate(sample = factor(sample, levels = sample_levels))

ends <- plot_data |> filter(year == max(year))

p <- ggplot(plot_data, aes(year, share, colour = sample, linetype = sample)) +
  geom_line(linewidth = 1.2) +
  geom_point(size = 2.8) +
  geom_text(data = ends, aes(label = percent(share, accuracy = 1)), hjust = -0.35, show.legend = FALSE, size = 3.8, fontface = "bold") +
  scale_colour_manual(values = setNames(c(pal$accent, pal$conc_mid), sample_levels), name = NULL) +
  scale_linetype_manual(values = setNames(c("solid", "dashed"), sample_levels), name = NULL) +
  scale_x_continuous(breaks = sort(unique(conc$year)), expand = expansion(mult = c(0.03, 0.08))) +
  scale_y_continuous(labels = percent, limits = c(0.3, 0.7)) +
  labs(
    title = "The recovery in competitive airports is not just new, smaller airports joining",
    subtitle = "Share of airports where the largest airline carries under 40% of passengers",
    x = NULL, y = "Share of airports that are competitive",
    caption = paste0(source_line, "\nAirlines are counted separately until they merged. Sample years shown.")
  ) +
  theme_story() +
  theme(legend.text = element_text(size = 10.5), axis.text.x = element_text(size = 10))

ggsave("figures/02b_airport_dominance_fixed.png", p, width = 10, height = 5.8, dpi = 200)