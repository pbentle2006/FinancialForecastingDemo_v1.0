"""
AI Insights Interface - Natural Language Query Interface
Provides chat-style interface for business intelligence queries
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from nlp_query_engine import NLPQueryEngine
from export_utilities import ExportUtilities
from typing import Dict, Any

class AIInsightsInterface:
    """Interactive interface for natural language business intelligence queries"""

    def __init__(self):
        self.query_engine = NLPQueryEngine()
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state for chat history"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        if 'current_query' not in st.session_state:
            st.session_state.current_query = ""

    def render_ai_insights(self, scenario_data: Dict = None):
        """Render the AI insights interface"""

        st.markdown("### 🤖 AI Business Intelligence")
        st.markdown("Ask natural language questions about your financial data and get AI-powered insights.")

        # Query input section
        self._render_query_input()

        # Chat history section
        self._render_chat_history()

        # Suggested questions section
        self._render_suggested_questions()

    def _render_query_input(self):
        """Render the query input interface"""

        st.markdown("#### 💬 Ask a Question")

        # Query input with submit button
        col1, col2 = st.columns([4, 1])

        with col1:
            query = st.text_input(
                "Enter your business question:",
                value=st.session_state.current_query,
                placeholder="e.g., 'How accurate are our forecasts?' or 'What are the biggest risks?'",
                key="query_input",
                label_visibility="collapsed"
            )

        with col2:
            submit_button = st.button("🚀 Ask AI", use_container_width=True, type="primary")

        # Process query if submitted
        if submit_button and query.strip():
            self._process_query(query.strip(), scenario_data=None)
            st.session_state.current_query = ""  # Clear input
            st.rerun()

    def _process_query(self, query: str, scenario_data: Dict = None):
        """Process a user query and add response to chat history"""

        # Show thinking animation
        with st.spinner("🤔 Analyzing your question..."):
            import time
            time.sleep(1)  # Simulate processing time

            # Get response from NLP engine
            response = self.query_engine.process_query(query, scenario_data)

        # Add to chat history
        chat_entry = {
            'timestamp': datetime.now(),
            'query': query,
            'response': response,
            'id': len(st.session_state.chat_history)
        }

        st.session_state.chat_history.append(chat_entry)

    def _render_chat_history(self):
        """Render the chat history"""

        if not st.session_state.chat_history:
            st.markdown("#### 📝 Chat History")
            st.info("💡 No questions asked yet. Try asking about forecast accuracy, risks, or performance!")
            return

        st.markdown("#### 📝 Chat History")

        # Display chat messages in reverse chronological order (newest first)
        for chat_entry in reversed(st.session_state.chat_history[-10:]):  # Show last 10 messages
            self._render_chat_message(chat_entry)

        # Clear history button
        if st.button("🗑️ Clear Chat History", help="Clear all previous questions and answers"):
            st.session_state.chat_history = []
            st.rerun()

        # Export chat history button
        if st.session_state.chat_history:
            if st.button("📤 Export Chat History", help="Export chat history and insights to Excel"):
                self._export_chat_history()

    def _export_chat_history(self):
        """Export chat history and insights to Excel"""
        try:
            export_utils = ExportUtilities()

            # Prepare chat history data for export
            chat_data = []
            for entry in st.session_state.chat_history:
                chat_data.append({
                    'Timestamp': entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'Question': entry['query'],
                    'Category': entry['response']['category'],
                    'Confidence': entry['response'].get('confidence', 0.5),
                    'Insights': '\n'.join(entry['response']['insights']),
                    'Recommendations': '\n'.join(entry['response'].get('recommendations', []))
                })

            chat_df = pd.DataFrame(chat_data)

            # Get insights summary
            insights_summary = self.get_insights_summary()

            # Prepare export data
            export_data = {
                'chat_history': chat_df,
                'insights_summary': insights_summary,
                'summary': [
                    f"Total AI queries: {insights_summary['total_queries']}",
                    f"Categories used: {', '.join(insights_summary['categories_used'])}",
                    f"Average confidence: {insights_summary['avg_confidence']:.1%}",
                    f"Most used category: {insights_summary['top_category'] or 'None'}",
                    f"Export generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                ]
            }

            # Export using the export utilities
            export_utils.add_export_button(
                export_data,
                button_text="📥 Download Chat History Excel",
                scenario_name="AI_Insights"
            )

        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")

    def _render_chat_message(self, chat_entry: Dict):
        """Render a single chat message"""

        with st.container():
            # User message
            with st.chat_message("user"):
                st.write(f"**You:** {chat_entry['query']}")

            # AI response
            with st.chat_message("assistant"):
                response = chat_entry['response']

                # Display category badge
                category_colors = {
                    'accuracy': '🟢',
                    'risk': '🟠',
                    'performance': '🔵',
                    'trend': '🟣',
                    'comparison': '🟡',
                    'summary': '⚪'
                }

                category_emoji = category_colors.get(response['category'], '🤖')
                st.markdown(f"**AI Analysis** {category_emoji} *{response['category'].title()}*")

                # Display insights
                for insight in response['insights']:
                    st.markdown(insight)

                # Display recommendations if available
                if 'recommendations' in response and response['recommendations']:
                    with st.expander("💡 Recommendations", expanded=False):
                        for rec in response['recommendations']:
                            st.markdown(f"• {rec}")

                # Display confidence score
                confidence = response.get('confidence', 0.5)
                confidence_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🟠"
                st.caption(f"Confidence: {confidence_color} {confidence:.1%}")

            st.markdown("---")

    def _render_suggested_questions(self):
        """Render suggested questions for users"""

        st.markdown("#### 💡 Suggested Questions")

        suggested_questions = self.query_engine.get_suggested_questions()

        # Create clickable buttons for suggested questions
        cols = st.columns(2)

        for i, question in enumerate(suggested_questions):
            col_idx = i % 2
            with cols[col_idx]:
                if st.button(
                    question,
                    key=f"suggested_{i}",
                    help="Click to ask this question",
                    use_container_width=True
                ):
                    self._process_query(question, scenario_data=None)
                    st.rerun()

        # Additional help text
        with st.expander("💡 How to Ask Questions", expanded=False):
            st.markdown("""
            **Try asking questions like:**
            - "How accurate are our revenue forecasts?"
            - "What are the biggest risks to our business?"
            - "Which projects are performing best?"
            - "What trends do you see in the data?"
            - "How do different scenarios compare?"
            - "What's the overall business outlook?"

            **The AI can analyze:**
            - 📊 Forecast accuracy and reliability
            - ⚠️ Business risks and opportunities
            - 📈 Performance trends and insights
            - 🔄 Scenario comparisons
            - 📋 Executive summaries
            """)

    def get_insights_summary(self) -> Dict[str, Any]:
        """Get a summary of insights from chat history"""

        if not st.session_state.chat_history:
            return {
                'total_queries': 0,
                'categories_used': [],
                'avg_confidence': 0.0,
                'top_category': None
            }

        queries = st.session_state.chat_history
        categories = [q['response']['category'] for q in queries]
        confidences = [q['response'].get('confidence', 0.5) for q in queries]

        # Count category usage
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1

        top_category = max(category_counts.items(), key=lambda x: x[1]) if category_counts else None

        return {
            'total_queries': len(queries),
            'categories_used': list(set(categories)),
            'avg_confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'top_category': top_category[0] if top_category else None,
            'category_breakdown': category_counts
        }
