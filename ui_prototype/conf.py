"""
Default Vowpal Wabbit configuration options
Each key in the dictionary corresponds to a `vw` command-line option
"""
vw_opts = {
    # General options
    "random_seed": 11399,
    # Input options
    "compressed": True,
    "save_resume": True,
    # Output options
    "progress": 1,
    "quiet": True,
    # Update rule options
    "loss_function": "logistic",
    # Other options
    "link": "logistic",
}
