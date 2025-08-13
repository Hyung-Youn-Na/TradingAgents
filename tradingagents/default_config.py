import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./output/20"),
    "data_dir": "/mnt/trading_agents/data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "ollama",
    "deep_think_llm": "qwen3:235b",
    "quick_think_llm": "llama3.2:3b",
    "backend_url": "http://10.1.203.33:11434/v1",
    # Debate and discussion settings
    "max_debate_rounds": 5,
    "max_risk_discuss_rounds": 5,
    "max_recur_limit": 200,
    # Tool settings
    "online_tools": False,
}
