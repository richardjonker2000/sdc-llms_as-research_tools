"""Helpers for the SDC 'LLMs as research tools' workshop."""
from .llm import (CFG, Extraction, SetupError, chat, decide, decide_many, embed, extract, extract_many, load_config, mode,
                  parse_json, quote_check, status)
from .style import COLORS, GREY, plot_confusion, plot_heatmap, setup_plots, show_diff
