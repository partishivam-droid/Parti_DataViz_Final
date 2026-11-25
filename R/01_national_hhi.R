source("R/theme.R")

hhi <- read_csv(file.path(data_dir, "national_concentration_as_reported.csv"), show_col_types = FALSE)

mergers <- tibble(
  year = c(2008, 2010, 2013),
  label = c("Delta + Northwest", "United + Continental", "American + US Airways")
)

p <- ggplot(hhi, aes(year, hhi)) +
  geom_vline(data = mergers, aes(xintercept = year), colour = pal$muted, linetype = "dashed", linewidth = 0.4) +
  geom_text(data = mergers, aes(x = year, y = 1680, label = label), angle = 90, hjust = 1, vjust = -0.4,
            colour = pal$muted, size = 3.6, inherit.aes = FALSE) +
  geom_line(colour = pal$accent, linewidth = 1.2) +
  geom_point(colour = pal$accent, size = 3) +
  scale_x_continuous(breaks = hhi$year, labels = hhi$year) +
  scale_y_continuous(labels = comma, limits = c(900, 1680)) +
  labs(
    title = "Air travel got about 40% more concentrated after the mergers",
    subtitle = "Higher means passengers are spread across fewer, larger airlines. Airlines counted separately until merger.",
    x = NULL, y = "Concentration index (HHI)",
    caption = paste0(source_line, "\nSample years shown. Independent regional airlines are grouped as one carrier. HHI = sum of squared market shares (percent).")
  ) +
  theme_story() +
  theme(axis.text.x = element_text(size = 10))

ggsave("figures/01_national_hhi.png", p, width = 9, height = 5.6, dpi = 200)
