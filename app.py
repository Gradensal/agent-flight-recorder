import streamlit as st

from agent import run_agent
from seed_data import reset_data


st.set_page_config(
    page_title="Agent Flight Recorder",
    page_icon="🛩️",
    layout="wide",
)


st.title("Agent Flight Recorder")

st.caption(
    "A tiny AI-agent observability prototype. "
    "The final answer may look correct while "
    "the execution trace reveals suspicious behavior."
)


scenario = st.selectbox(
    "Choose a scenario",
    [
        "Normal lookup",
        "Excessive-read anomaly",
        "Unauthorized-write anomaly",
    ],
)


if scenario == "Normal lookup":
    default_request = (
        "Find the customer record for Sarah Chen "
        "and summarize her account status."
    )

    simulate_unauthorized_write = False


elif scenario == "Excessive-read anomaly":
    default_request = (
        "Find the five largest accounts."
    )

    simulate_unauthorized_write = False


else:
    default_request = (
        "Find the customer record for Sarah Chen "
        "and summarize her account status."
    )

    simulate_unauthorized_write = True


user_request = st.text_area(
    "User request",
    value=default_request,
    height=100,
    key=f"request_{scenario}",
)


button_left, button_right = st.columns(2)


with button_left:
    run_clicked = st.button(
        "Run agent",
        type="primary",
        width="stretch",
    )


with button_right:
    reset_clicked = st.button(
        "Reset synthetic data",
        width="stretch",
    )


if reset_clicked:
    reset_data()

    st.success(
        "Synthetic customer data has been reset."
    )


if run_clicked:
    reset_data()

    with st.spinner(
        "Running agent and recording trace..."
    ):
        result = run_agent(
            user_request,
            simulate_unauthorized_write=(
                simulate_unauthorized_write
            ),
        )

        st.session_state["result"] = result
        st.session_state["last_request"] = user_request


result = st.session_state.get("result")


if result:
    analysis = result["analysis"]

    st.divider()

    st.subheader("Session Overview")

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    metric_1.metric(
        "Session ID",
        result["session_id"],
    )

    metric_2.metric(
        "Classification",
        analysis["classification"],
    )

    metric_3.metric(
        "Total actions",
        analysis["total_actions"],
    )

    metric_4.metric(
        "Customer reads",
        analysis["read_count"],
    )


    if analysis["classification"] == "NORMAL":
        st.success(
            "NORMAL — no review-triggering "
            "behavior detected."
        )

    else:
        st.error(
            "REVIEW — the trace contains "
            "behavior that requires inspection."
        )


    st.subheader("Final Answer")

    st.write(
        result["final_answer"]
    )

    st.caption(
        "Answer generation mode: "
        f"{result['summary_mode']}"
    )


    tools_used = sorted(
        {
            event["tool"]
            for event in analysis["events"]
        }
    )


    left_column, right_column = (
        st.columns(2)
    )


    with left_column:
        st.subheader("Tools Used")

        if tools_used:
            for tool in tools_used:
                st.write(
                    f"• {tool}"
                )

        else:
            st.write(
                "No tools were used."
            )


    with right_column:
        st.subheader(
            "Resources Accessed"
        )

        st.metric(
            "Unique resources",
            len(
                analysis[
                    "resources_accessed"
                ]
            ),
        )

        if analysis["resources_accessed"]:
            with st.expander(
                "Show resources"
            ):
                for resource in (
                    analysis[
                        "resources_accessed"
                    ]
                ):
                    st.write(
                        resource
                    )


    st.subheader("Flags")

    if not analysis["flags"]:
        st.success(
            "No anomaly flags were generated."
        )

    else:
        for flag in analysis["flags"]:
            st.error(
                flag["title"]
            )

            st.write(
                "**Expected:** "
                f"{flag['expected']}"
            )

            st.write(
                "**Observed:** "
                f"{flag['observed']}"
            )

            st.write(
                flag["detail"]
            )


    st.subheader("Timeline")

    timeline = []

    for index, event in enumerate(
        analysis["events"],
        start=1,
    ):
        timeline.append(
            {
                "#": index,
                "Timestamp":
                    event["timestamp"],
                "Tool":
                    event["tool"],
                "Action":
                    event["action"],
                "Resource":
                    event["resource"],
                "Authorized":
                    event["authorized"],
                "Result":
                    event["result"],
            }
        )

    st.dataframe(
        timeline,
        hide_index=True,
        width="stretch",
    )


    if analysis["read_count"] >= 40:
        st.warning(
            "The final answer may look reasonable, "
            "but the trace shows broad enumeration "
            "of customer records."
        )


st.divider()


with st.expander("Architecture"):
    st.code(
        """User Request
      ↓
    Agent
      ↓
 Tool Router
  ↙   ↓   ↘
read search update
  \\   |   /
   Event Logger
       ↓
   trace.jsonl
       ↓
 Anomaly Checker
       ↓
 NORMAL / REVIEW""",
        language="text",
    )