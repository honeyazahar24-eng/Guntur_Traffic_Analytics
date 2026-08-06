import streamlit as st


class UI:

    # ==========================================================
    # Section Title
    # ==========================================================

    @staticmethod
    def section(title, icon=""):

        if icon:
            st.markdown(f"## {icon} {title}")
        else:
            st.markdown(f"## {title}")

    # ==========================================================
    # Card Container
    # ==========================================================

    @staticmethod
    def begin_card():

        st.markdown(
            """
            <div class="dashboard-card">
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def end_card():

        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True
        )

    # ==========================================================
    # Empty State
    # ==========================================================

    @staticmethod
    def empty(message="No data available"):

        st.info(message)

    # ==========================================================
    # Success
    # ==========================================================

    @staticmethod
    def success(message):

        st.success(message)

    # ==========================================================
    # Warning
    # ==========================================================

    @staticmethod
    def warning(message):

        st.warning(message)

    # ==========================================================
    # Error
    # ==========================================================

    @staticmethod
    def error(message):

        st.error(message)

    # ==========================================================
    # Divider
    # ==========================================================

    @staticmethod
    def divider():

        st.divider()