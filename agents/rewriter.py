from langchain.schema import HumanMessage


def rewriter_node(llm):
    def rewriter_fn(state):
        advisories = state.get("reasoning_result", [])
        print(advisories)
        dates_raw = [k.get("date_raw")for k in state.get("plannification", [])]
        input_summary = "\n".join([
            f"At {dates_raw[idx]} corresponding {a['dates']} and {a['location']}: {a['summaries']} (Action: {a['actions']}, Reason: {a['reasons']})"
            for idx, a in enumerate(advisories)
        ])

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
