QUESTIONS = [
    {
        "business": "corner",
        "question": "Will I run low on cash?",
        "must_mention": ["week 11", "9,000"],
        "tool": "get_flags",
    },
    {
        "business": "corner",
        "question": "Which expense should I look at first?",
        "must_mention": ["inventory"],
        "tool": "get_flags",
    },
    {
        "business": "corner",
        "question": "What happens if my sales drop for a month?",
        "must_mention": ["slow"],
        "tool": "run_scenario",
    },
    {
        "business": "taqueria",
        "question": "How much cash will I have in 13 weeks?",
        "must_mention": ["week 13"],
        "tool": "get_forecast",
    },
    {
        "business": "taqueria",
        "question": "Is any one cost too big a share of my spending?",
        "must_mention": ["supplies"],                
        "tool": "get_flags",
    },
]