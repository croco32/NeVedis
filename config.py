"""Shared settings for NeVedis. Change the model here and nowhere else."""

# Main model. gemini-3.8-flash (newest) and gemini-3.7-flash timed out on Google's side on
# Nov 8, 2026 (503/504). To try the newest again, change this line to: MODEL = "gemini-3.8-flash"
MODEL = "gemini-3.6-flash"

# Tried in order when the main model is out of quota or busy (429/503). On Google's free
# plan each model has its own daily limit (20 checks/day), so backups multiply capacity.
BACKUP_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
