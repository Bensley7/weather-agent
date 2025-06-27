

def router_node():
    def route(state):
        qtype = state.get("question_type", "daily_summary")
        if qtype == "find_extreme":
            return "extreme_reasoner_node"
        elif qtype == "activity_feasibility":
            return "activity_reasoner_node"
        else:
            return "summary_reasoner_node"  # default
    return route
