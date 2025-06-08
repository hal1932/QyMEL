def current_file_path():
    import inspect
    return inspect.currentframe().f_back.f_code.co_filename
