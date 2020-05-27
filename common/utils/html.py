def html(e, txt, attributes = None):
	
    properties = ""
    if attributes:
        properties = " ".join([
            "=".join([key, f"'{value}'"])
            for key, value in attributes.items()
        ])

    return f"""<{e} {properties}>{txt}</{e}>"""