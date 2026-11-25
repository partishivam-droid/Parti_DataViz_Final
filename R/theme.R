library(ggplot2)
library(dplyr)
library(readr)
library(scales)

pal <- list(
  # airlines
  united    = "#0A5DC2",
  american  = "#D2232A",
  delta     = "#0B2A57",
  southwest = "#F2A900",
  alaska    = "#00A0AF",
  jetblue   = "#5CB8E6",
  spirit    = "#E5C200",
  frontier  = "#2E8B57",
  allegiant = "#E8710A",
  hawaiian  = "#6B3FA0",
  other     = "#9CA3AF",
  us_airways   = "#DD5A5F",
  america_west = "#E89194",
  twa          = "#F2C1C3",
  northwest    = "#607592",
  continental  = "#78A6DD",
  airtran      = "#F8D480",
  other_light  = "#D1D5DB",

  # non-airline elements
  accent    = "#374151",
  muted     = "#6B7280",
  ink       = "#1F2937",
  grid      = "#E5E7EB",
  bg        = "#FFFFFF",
  conc_low  = "#CBD5E1",
  conc_mid  = "#64748B",
  conc_high = "#1E293B"
)

theme_story <- function(base_size = 13, base_family = "sans") {
  theme_minimal(base_size = base_size, base_family = base_family) +
    theme(
      plot.background = element_rect(fill = pal$bg, colour = NA),
      panel.background = element_rect(fill = pal$bg, colour = NA),
      panel.grid.major = element_line(colour = pal$grid, linewidth = 0.4),
      panel.grid.minor = element_blank(),
      text = element_text(colour = pal$ink),
      plot.title = element_text(face = "bold", size = base_size + 4, hjust = 0, margin = margin(b = 4)),
      plot.subtitle = element_text(colour = pal$muted, hjust = 0, margin = margin(b = 10)),
      plot.caption = element_text(colour = pal$muted, size = base_size - 3, hjust = 0, margin = margin(t = 10)),
      plot.title.position = "plot",
      plot.caption.position = "plot",
      axis.title = element_text(colour = pal$muted, size = base_size - 1),
      legend.position = "bottom",
      plot.margin = margin(14, 16, 10, 14)
    )
}

source_line <- "Source: U.S. Bureau of Transportation Statistics, T-100 Domestic Market (U.S. carriers); author's calculations."

data_dir <- "data/processed"