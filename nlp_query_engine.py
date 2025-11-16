"""
NLP Query Engine - Natural Language Processing for Financial Insights
Provides business intelligence through natural language queries
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

class NLPQueryEngine:
    """Engine for processing natural language queries about financial data"""

    def __init__(self, data_source=None):
        self.data_source = data_source
        self.query_patterns = {
            # Accuracy queries
            'accuracy': [
                r'how accurate.*forecast',
                r'forecast accuracy',
                r'mape|mean absolute.*error',
                r'prediction.*error'
            ],

            # Risk queries
            'risk': [
                r'risk.*analysis',
                r'high.*risk',
                r'risk.*factor',
                r'risky.*project'
            ],

            # Performance queries
            'performance': [
                r'best.*performing',
                r'top.*performing',
                r'worst.*performing',
                r'performance.*analysis',
                r'how.*performing'
            ],

            # Trend queries
            'trend': [
                r'trend.*analysis',
                r'what.*trend',
                r'growth.*trend',
                r'declining.*trend'
            ],

            # Comparison queries
            'comparison': [
                r'compare.*scenario',
                r'vs|versus|compared.*to',
                r'difference.*between',
                r'better.*than'
            ],

            # Summary queries
            'summary': [
                r'summarize|summary',
                r'overview|key.*insights',
                r'what.*happening',
                r'tell.*me.*about'
            ]
        }

    def process_query(self, query: str, scenario_data: Dict = None) -> Dict[str, Any]:
        """
        Process a natural language query and return insights

        Args:
            query: Natural language query string
            scenario_data: Current scenario data context

        Returns:
            Dict with response, insights, and metadata
        """
        query_lower = query.lower().strip()

        # Determine query category
        category = self._categorize_query(query_lower)

        # Generate response based on category
        response = self._generate_response(category, query_lower, scenario_data)

        return {
            'query': query,
            'category': category,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'confidence': self._calculate_confidence(category, query_lower)
        }

    def _categorize_query(self, query: str) -> str:
        """Categorize the query based on pattern matching"""
        for category, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return category

        # Default to summary if no specific category matches
        return 'summary'

    def _generate_response(self, category: str, query: str, scenario_data: Dict = None) -> Dict[str, Any]:
        """Generate a response based on query category"""

        if category == 'accuracy':
            return self._accuracy_response(query, scenario_data)
        elif category == 'risk':
            return self._risk_response(query, scenario_data)
        elif category == 'performance':
            return self._performance_response(query, scenario_data)
        elif category == 'trend':
            return self._trend_response(query, scenario_data)
        elif category == 'comparison':
            return self._comparison_response(query, scenario_data)
        else:  # summary
            return self._summary_response(query, scenario_data)

    def _accuracy_response(self, query: str, scenario_data: Dict = None) -> Dict[str, Any]:
        """Generate accuracy analysis response"""
        insights = []

        # Mock accuracy metrics (would be calculated from actual data)
        accuracy_metrics = {
            'mape': np.random.uniform(5, 15),  # 5-15% MAPE
            'bias': np.random.uniform(-2, 2),   # -2% to +2% bias
            'confidence_interval': 95
        }

        insights.append(f"📊 Forecast Accuracy Analysis:")
        insights.append(f"• Mean Absolute Percentage Error (MAPE): {accuracy_metrics['mape']:.1f}%")
        insights.append(f"• Forecast Bias: {accuracy_metrics['bias']:+.1f}%")
        insights.append(f"• Confidence Interval: {accuracy_metrics['confidence_interval']}%")

        if accuracy_metrics['mape'] < 10:
            insights.append("✅ Excellent forecast accuracy (<10% MAPE)")
        elif accuracy_metrics['mape'] < 20:
            insights.append("⚠️ Good forecast accuracy (10-20% MAPE)")
        else:
            insights.append("❌ Forecast accuracy needs improvement (>20% MAPE)")

        return {
            'type': 'accuracy_analysis',
            'insights': insights,
            'metrics': accuracy_metrics,
            'recommendations': [
                "Consider using more granular historical data for better accuracy",
                "Implement rolling forecast updates for improved precision"
            ]
        }

    def _risk_response(self, query: str, scenario_data: Dict = None) -> Dict[str, Any]:
        """Generate risk analysis response"""
        insights = []

        # Mock risk assessment
        risk_factors = {
            'high_risk_projects': np.random.randint(2, 5),
            'revenue_concentration': np.random.uniform(30, 60),
            'forecast_volatility': np.random.uniform(10, 25)
        }

        insights.append(f"⚠️ Risk Assessment:")
        insights.append(f"• High-risk projects identified: {risk_factors['high_risk_projects']}")
        insights.append(f"• Revenue concentration risk: {risk_factors['revenue_concentration']:.1f}%")
        insights.append(f"• Forecast volatility: {risk_factors['forecast_volatility']:.1f}%")

        if risk_factors['revenue_concentration'] > 50:
            insights.append("🚨 High revenue concentration - diversify client base")
        if risk_factors['forecast_volatility'] > 20:
            insights.append("📈 High forecast volatility - consider scenario planning")

        return {
            'type': 'risk_analysis',
            'insights': insights,
            'risk_factors': risk_factors,
            'recommendations': [
                "Diversify revenue streams to reduce concentration risk",
                "Implement risk mitigation strategies for high-risk projects",
                "Use multiple scenarios to account for forecast uncertainty"
            ]
        }

    def _performance_response(self, query: str, scenario_data: Dict = None) -> Dict[str, Any]:
        """Generate performance analysis response"""
        insights = []

        # Mock performance data
        top_performers = [
            {"name": "Enterprise Client A", "growth": 45.2},
            {"name": "Tech Solutions Inc", "growth": 38.7},
            {"name": "Global Corp", "growth": 31.1}
        ]

        underperformers = [
            {"name": "Legacy Systems Ltd", "decline": -12.3},
            {"name": "Traditional Co", "decline": -8.9}
        ]

        insights.append("🏆 Performance Highlights:")
        insights.append("**Top Performers:**")
        for performer in top_performers:
            insights.append(f"• {performer['name']}: +{performer['growth']:.1f}% growth")

        insights.append("**Areas of Concern:**")
        for underperformer in underperformers:
            insights.append(f"• {underperformer['name']}: {underperformer['decline']:.1f}% decline")

        return {
            'type': 'performance_analysis',
            'insights': insights,
            'top_performers': top_performers,
            'underperformers': underperformers,
            'recommendations': [
                "Invest more resources in top-performing segments",
                "Investigate causes of underperformance",
                "Consider strategic adjustments for declining areas"
            ]
        }

    def _trend_response(self, query: str, scenario_data: Dict = None) -> Dict[str, Any]:
        """Generate trend analysis response"""
        insights = []

        # Mock trend data
        trends = {
            'overall_growth': np.random.uniform(15, 35),
            'seasonal_pattern': 'Q4 peak, Q1-Q2 growth',
            'emerging_segments': ['Cloud Services', 'AI Solutions'],
            'declining_segments': ['Legacy Systems']
        }

        insights.append(f"📈 Trend Analysis:")
        insights.append(f"• Overall revenue growth trend: {trends['overall_growth']:.1f}% annually")
        insights.append(f"• Seasonal pattern: {trends['seasonal_pattern']}")
        insights.append(f"• Emerging high-growth segments: {', '.join(trends['emerging_segments'])}")
        insights.append(f"• Declining segments: {', '.join(trends['declining_segments'])}")

        return {
            'type': 'trend_analysis',
            'insights': insights,
            'trends': trends,
            'recommendations': [
                "Focus investment in emerging high-growth segments",
                "Develop strategies to revitalize declining segments",
                "Leverage seasonal patterns in forecasting and planning"
            ]
        }

    def _comparison_response(self, query: str, scenario_data: Dict = None) -> Dict[str, Any]:
        """Generate comparison analysis response"""
        insights = []

        # Mock comparison data
        scenarios = {
            'base_case': {'revenue': 125.5, 'margin': 28.3},
            'optimistic': {'revenue': 142.8, 'margin': 31.7},
            'conservative': {'revenue': 108.9, 'margin': 25.1}
        }

        insights.append("⚖️ Scenario Comparison:")
        for scenario, metrics in scenarios.items():
            insights.append(f"• {scenario.title()}: ${metrics['revenue']:.1f}M revenue, {metrics['margin']:.1f}% margin")

        best_scenario = max(scenarios.items(), key=lambda x: x[1]['revenue'])
        insights.append(f"💡 Best performing scenario: {best_scenario[0].title()}")

        return {
            'type': 'comparison_analysis',
            'insights': insights,
            'scenarios': scenarios,
            'recommendations': [
                f"Consider planning for {best_scenario[0].title()} scenario outcomes",
                "Use scenario analysis for risk management",
                "Prepare contingency plans for different outcomes"
            ]
        }

    def _summary_response(self, query: str, scenario_data: Dict = None) -> Dict[str, Any]:
        """Generate summary/overview response"""
        insights = []

        # Mock summary data
        summary_stats = {
            'total_revenue': np.random.uniform(100, 150),
            'total_projects': np.random.randint(50, 80),
            'avg_project_size': np.random.uniform(2.5, 4.5),
            'forecast_period': '8 quarters',
            'key_drivers': ['Digital transformation', 'Cloud migration', 'AI adoption']
        }

        insights.append("📊 Executive Summary:")
        insights.append(f"• Total forecasted revenue: ${summary_stats['total_revenue']:.1f}M")
        insights.append(f"• Active projects: {summary_stats['total_projects']}")
        insights.append(f"• Average project size: ${summary_stats['avg_project_size']:.1f}M")
        insights.append(f"• Forecast horizon: {summary_stats['forecast_period']}")
        insights.append(f"• Key growth drivers: {', '.join(summary_stats['key_drivers'])}")

        return {
            'type': 'executive_summary',
            'insights': insights,
            'summary_stats': summary_stats,
            'recommendations': [
                "Focus on key growth drivers for maximum impact",
                "Monitor project pipeline for consistent revenue flow",
                "Use forecasting insights for strategic decision making"
            ]
        }

    def _calculate_confidence(self, category: str, query: str) -> float:
        """Calculate confidence score for the response"""
        # Simple confidence calculation based on pattern matching strength
        if category in ['accuracy', 'risk', 'performance']:
            return 0.85  # High confidence for specific analysis queries
        elif category in ['trend', 'comparison']:
            return 0.75  # Medium-high confidence
        else:
            return 0.65  # Medium confidence for general queries

    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions for users"""
        return [
            "How accurate are our revenue forecasts?",
            "What are the biggest risks to our revenue?",
            "Which projects are performing best?",
            "What are the key revenue trends?",
            "How do different scenarios compare?",
            "What's the overall business outlook?"
        ]
