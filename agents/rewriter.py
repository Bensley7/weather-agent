from langchain.schema import HumanMessage


def rewriter_node(llm):
    def rewriter_fn(state):
    
        advisories = state.get("reasoning_result", [])
        dates_raw = [k.get("date_raw")for k in state.get("plannification", [])]

        input_summary = ""

        for idx, advisory in enumerate(advisories):
            location = advisory["location"]
            date_list = advisory["dates"]
            summary = advisory["summaries"]
            action = advisory["actions"]
            reason = advisory["reasons"]
            decision = advisory["decision"]

            # Optional: fetch raw input dates if needed
            raw_date = dates_raw[idx] if idx < len(dates_raw) else ", ".join(date_list)

            if decision:
                input_summary += (
                    f"\n→ At {raw_date} ({location}):\n"
                    f"  Answer: {decision} and {summary}  \n"
                    f"  Reason: {reason}\n"
                )
            else:
                input_summary += (
                    f"\n→ At {raw_date} ({location}):\n"
                    f"  Summary: {summary}\n"
                    f"  Suggested Action: {action}\n"
                    f"  Reason: {reason}\n"
                )

        prompt = f"""
            You are a helpful assistant. Summarize the following city-level weather advice into a friendly, readable response.
            Show the date when necessary, and show weather data if the intent is temperature check. Generally speacking don't show 
            date as in 21 July 2025.

            City summaries:
            {input_summary}

            Respond to the user.
        """

        response = llm.invoke([HumanMessage(content=prompt)])
        return {"ai_writer_result": response.content}

    return rewriter_fn
