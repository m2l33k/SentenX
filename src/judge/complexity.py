import radon.complexity as cc

def get_complexity_score(code_str):
    """
    Calculates Cyclomatic Complexity.
    Lower score = Simpler code (Better).
    1-5: Simple, 6-10: Complex, 11+: Very Complex
    """
    try:
        # Analyze the code string
        results = cc.cc_visit(code_str)
        if not results:
            return 100 # Penalty if code is unparseable
        
        # Return the complexity of the first function found
        return results[0].complexity
    except Exception as e:
        print(f"Complexity Error: {e}")
        return 100 # High penalty for broken code