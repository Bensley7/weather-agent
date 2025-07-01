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
            Tu es un assistant utile. Résume les conseils météo suivants, ville par ville, dans une réponse conviviale et facile à lire.

            Affiche la date uniquement si cela est nécessaire, et indique les données météo lorsque l’intention concerne la température. De manière générale, n’affiche pas les dates sous la forme "21 juillet 2025".

            Résumés par ville :
            {input_summary}

            Réponds à l’utilisateur.
        """

        response = llm.invoke([HumanMessage(content=prompt)])
        return {"ai_writer_result": response.content}

    return rewriter_fn
