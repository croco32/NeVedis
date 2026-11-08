"""Shared settings for NeVedis. Change the model here and nowhere else."""

# gemini-3.8-flash (newest) and gemini-3.7-flash timed out on Google's side on Nov 8, 2026
# (503 high demand / 504 deadline exceeded). gemini-3.6-flash answers in ~4 s.
# To try the newest again, change this line to: MODEL = "gemini-3.8-flash"
MODEL = "gemini-3.6-flash"
