source("R/theme.R")

shares <- read_csv(file.path(data_dir, "national_share_as_reported_grouped.csv"), show_col_types = FALSE)

lookup <- tribble(
  ~carrier,                          ~airline,                ~family,
  "American Airlines Inc.",          "American",              "American",
  "US Airways Inc.",                 "US Airways",            "American",
  "USAir Shuttle",                   "US Airways",            "American",
  "America West Airlines Inc.",      "America West",          "American",
  "Trans World Airways LLC",         "TWA",                   "American",
  "Delta Air Lines Inc.",            "Delta",                 "Delta",
  "Northwest Airlines Inc.",         "Northwest",             "Delta",
  "United Air Lines Inc.",           "United",                "United",
  "Continental Air Lines Inc.",      "Continental",           "United",
  "Continental Micronesia",          "Continental",           "United",
  "Southwest Airlines Co.",          "Southwest",             "Southwest",
  "AirTran Airways Corporation",     "AirTran",               "Southwest",
  "Regional (independent)",          "Independent regionals", "Regional"
)

fills <- c(
  "American" = pal$american, "US Airways" = pal$us_airways, "America West" = pal$america_west, "TWA" = pal$twa,
  "Delta" = pal$delta, "Northwest" = pal$northwest,
  "United" = pal$united, "Continental" = pal$continental,
  "Southwest" = pal$southwest, "AirTran" = pal$airtran,
  "Independent regionals" = pal$other, "Other airlines" = pal$other_light
)

light_fills <- c("America West", "TWA", "Continental", "Southwest", "AirTran", "Independent regionals", "Other airlines")

plot_data <- shares |>
  left_join(lookup, by = "carrier") |>
  mutate(airline = coalesce(airline, "Other airlines")) |>
  group_by(year, airline) |>
  summarise(share = sum(share), .groups = "drop") |>
  mutate(airline = factor(airline, levels = names(fills))) |>
  arrange(year, airline) |>
  group_by(year) |>
  mutate(top = cumsum(share), bottom = top - share, mid = (top + bottom) / 2) |>
  ungroup() |>
  mutate(year_f = factor(year),
         airline_stack = factor(as.character(airline), levels = rev(names(fills))),
         label = recode(as.character(airline), "Independent regionals" = "Regionals", "Other airlines" = "Other"),
         label_colour = if_else(as.character(airline) %in% light_fills, pal$ink, "white"))

p <- ggplot(plot_data, aes(year_f, share, fill = airline_stack)) +
  geom_col(width = 0.82, colour = pal$bg, linewidth = 0.5) +
  geom_text(data = filter(plot_data, share >= 0.04),
            aes(x = year_f, y = mid, label = label, colour = label_colour),
            size = 3.2, fontface = "bold", inherit.aes = FALSE) +
  scale_fill_manual(values = fills, guide = "none") +
  scale_colour_identity() +
  scale_y_continuous(labels = percent, expand = expansion(mult = c(0, 0.01))) +
  labs(
    title = "The Number of Airlines Serving U.S. Domestic Passengers Fell 50% After the Mergers",
    subtitle = "Share of U.S. domestic passengers. Shades of one color are airlines that later became part of the same company.",
    x = NULL, y = "Share of domestic passengers",
    caption = paste0(source_line, "\nSample years shown. Labels shown for shares of 4% or more. Independent regional airlines are grouped together.")
  ) +
  theme_story() +
  theme(panel.grid.major.x = element_blank())

ggsave("figures/03_airline_share.png", p, width = 10, height = 6.2, dpi = 200)