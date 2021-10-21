try:
    import catprinter.catprinter.cmds
    import catprinter.catprinter.ble
    import catprinter.catprinter.img
except Exception as e:
    # Couldn't load as a pip package. Trying standalone
    import catprinter.cmds
    import catprinter.ble
    import catprinter.img
