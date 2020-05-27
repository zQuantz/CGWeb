
def html(e, txt, attributes = None):
	
    properties = ""
    if attributes:
        properties = " ".join([
            "=".join([key, f"'{value}'"])
            for key, value in attributes.items()
        ])
        properties = " " + properties

    return f"""<{e}{properties}>{txt}</{e}>"""