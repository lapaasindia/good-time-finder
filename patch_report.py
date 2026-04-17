with open("app/services/report_generator.py", "r") as f:
    text = f.read()

old_code = """        # Dasha periods use naive datetimes from birth_datetime; normalise for comparison
        naive_dt = current_dt.replace(tzinfo=None) if current_dt.tzinfo else current_dt
        for maha in mahas:
            if maha.end > naive_dt:"""

new_code = """        comparison_dt = current_dt
        for maha in mahas:
            comp_maha_end = maha.end
            if maha.end.tzinfo is None and comparison_dt.tzinfo is not None:
                comp_maha_end = maha.end.replace(tzinfo=comparison_dt.tzinfo)
            elif maha.end.tzinfo is not None and comparison_dt.tzinfo is None:
                comp_maha_end = maha.end.replace(tzinfo=None)

            if comp_maha_end > comparison_dt:"""

text = text.replace(old_code, new_code)
with open("app/services/report_generator.py", "w") as f:
    f.write(text)
