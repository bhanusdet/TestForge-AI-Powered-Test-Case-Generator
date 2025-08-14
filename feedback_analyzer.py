#!/usr/bin/env python3
"""
🔍 Feedback Analysis Tool
Analyzes feedback patterns and provides insights for system improvement
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from backend.enhanced_rag_helper import rag_helper

class FeedbackAnalyzer:
    def __init__(self):
        self.rag_helper = rag_helper
    
    def analyze_feedback_patterns(self) -> dict:
        """Comprehensive feedback analysis"""
        print("🔍 Analyzing feedback patterns...")
        
        try:
            # Get all feedback data
            feedback_results = self.rag_helper.feedback_collection.get()
            
            if not feedback_results['metadatas']:
                return {"error": "No feedback data available"}
            
            analysis = {
                "summary": self._get_summary_stats(feedback_results),
                "quality_patterns": self._analyze_quality_patterns(feedback_results),
                "category_insights": self._analyze_category_patterns(feedback_results),
                "improvement_opportunities": self._identify_improvement_opportunities(feedback_results),
                "user_satisfaction_trend": self._analyze_satisfaction_trends(feedback_results)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def _get_summary_stats(self, feedback_results: dict) -> dict:
        """Get basic summary statistics"""
        metadatas = feedback_results['metadatas']
        
        quality_scores = [float(m.get('quality_score', 3.0)) for m in metadatas]
        
        return {
            "total_feedback": len(metadatas),
            "avg_quality_score": round(sum(quality_scores) / len(quality_scores), 2),
            "quality_distribution": {
                "excellent (5)": sum(1 for s in quality_scores if s == 5.0),
                "good (4)": sum(1 for s in quality_scores if s == 4.0),
                "average (3)": sum(1 for s in quality_scores if s == 3.0),
                "below_avg (2)": sum(1 for s in quality_scores if s == 2.0),
                "poor (1)": sum(1 for s in quality_scores if s == 1.0)
            }
        }
    
    def _analyze_quality_patterns(self, feedback_results: dict) -> dict:
        """Analyze patterns in quality scores"""
        metadatas = feedback_results['metadatas']
        
        # Group by time periods
        recent_scores = []
        older_scores = []
        
        cutoff_date = datetime.now() - timedelta(days=7)  # Last 7 days
        
        for metadata in metadatas:
            try:
                date_str = metadata.get('feedback_date', datetime.now().isoformat())
                feedback_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                quality_score = float(metadata.get('quality_score', 3.0))
                
                if feedback_date > cutoff_date:
                    recent_scores.append(quality_score)
                else:
                    older_scores.append(quality_score)
            except:
                continue
        
        recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 3.0
        older_avg = sum(older_scores) / len(older_scores) if older_scores else 3.0
        
        return {
            "recent_week_avg": round(recent_avg, 2),
            "historical_avg": round(older_avg, 2),
            "trend": "improving" if recent_avg > older_avg + 0.1 else "declining" if recent_avg < older_avg - 0.1 else "stable",
            "recent_feedback_count": len(recent_scores),
            "improvement_rate": round(recent_avg - older_avg, 2)
        }
    
    def _analyze_category_patterns(self, feedback_results: dict) -> dict:
        """Analyze feedback categories"""
        metadatas = feedback_results['metadatas']
        
        category_issues = defaultdict(int)
        category_quality_map = defaultdict(list)
        
        for metadata in metadatas:
            quality_score = float(metadata.get('quality_score', 3.0))
            categories_str = metadata.get('feedback_categories', '[]')
            
            try:
                categories = json.loads(categories_str) if categories_str else []
                for category in categories:
                    category_issues[category] += 1
                    category_quality_map[category].append(quality_score)
            except:
                continue
        
        category_analysis = {}
        for category, count in category_issues.items():
            avg_quality = sum(category_quality_map[category]) / len(category_quality_map[category])
            category_analysis[category] = {
                "mention_count": count,
                "avg_quality_when_mentioned": round(avg_quality, 2),
                "severity": "high" if avg_quality < 2.5 else "medium" if avg_quality < 3.5 else "low"
            }
        
        return category_analysis
    
    def _identify_improvement_opportunities(self, feedback_results: dict) -> list:
        """Identify key improvement opportunities"""
        metadatas = feedback_results['metadatas']
        
        opportunities = []
        
        # Analyze low-quality feedback for patterns
        low_quality_feedback = [m for m in metadatas if float(m.get('quality_score', 3.0)) <= 2.0]
        
        if len(low_quality_feedback) > len(metadatas) * 0.2:  # More than 20% low quality
            opportunities.append({
                "priority": "HIGH",
                "issue": "High rate of low-quality ratings",
                "impact": f"{len(low_quality_feedback)} out of {len(metadatas)} ratings are ≤2",
                "recommendation": "Focus on improving base test case generation quality"
            })
        
        # Analyze common missing scenarios
        missing_scenarios = defaultdict(int)
        for metadata in metadatas:
            missing_str = metadata.get('missing_scenarios', '[]')
            try:
                missing_list = json.loads(missing_str) if missing_str else []
                for scenario in missing_list:
                    if scenario.strip():
                        missing_scenarios[scenario.strip().lower()] += 1
            except:
                continue
        
        if missing_scenarios:
            top_missing = sorted(missing_scenarios.items(), key=lambda x: x[1], reverse=True)[:3]
            for scenario, count in top_missing:
                opportunities.append({
                    "priority": "MEDIUM",
                    "issue": f"Commonly missing scenario: {scenario}",
                    "impact": f"Mentioned in {count} feedback submissions",
                    "recommendation": f"Enhance prompts to include {scenario} scenarios"
                })
        
        return opportunities
    
    def _analyze_satisfaction_trends(self, feedback_results: dict) -> dict:
        """Analyze user satisfaction over time"""
        metadatas = feedback_results['metadatas']
        
        # Group by week
        weekly_scores = defaultdict(list)
        
        for metadata in metadatas:
            try:
                date_str = metadata.get('feedback_date', datetime.now().isoformat())
                feedback_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                quality_score = float(metadata.get('quality_score', 3.0))
                
                # Get week start (Monday)
                week_start = feedback_date - timedelta(days=feedback_date.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                
                weekly_scores[week_key].append(quality_score)
            except:
                continue
        
        # Calculate weekly averages
        weekly_averages = {}
        for week, scores in weekly_scores.items():
            weekly_averages[week] = round(sum(scores) / len(scores), 2)
        
        # Sort by date
        sorted_weeks = sorted(weekly_averages.items())
        
        return {
            "weekly_averages": dict(sorted_weeks),
            "total_weeks": len(sorted_weeks),
            "trend_direction": self._calculate_trend_direction(sorted_weeks)
        }
    
    def _calculate_trend_direction(self, sorted_weeks: list) -> str:
        """Calculate overall trend direction"""
        if len(sorted_weeks) < 2:
            return "insufficient_data"
        
        first_half_avg = sum(score for _, score in sorted_weeks[:len(sorted_weeks)//2]) / (len(sorted_weeks)//2)
        second_half_avg = sum(score for _, score in sorted_weeks[len(sorted_weeks)//2:]) / (len(sorted_weeks) - len(sorted_weeks)//2)
        
        if second_half_avg > first_half_avg + 0.2:
            return "strongly_improving"
        elif second_half_avg > first_half_avg + 0.1:
            return "improving"
        elif second_half_avg < first_half_avg - 0.2:
            return "strongly_declining"
        elif second_half_avg < first_half_avg - 0.1:
            return "declining"
        else:
            return "stable"
    
    def generate_report(self) -> str:
        """Generate a comprehensive feedback analysis report"""
        analysis = self.analyze_feedback_patterns()
        
        if "error" in analysis:
            return f"❌ Analysis Error: {analysis['error']}"
        
        report = []
        report.append("🔍 FEEDBACK ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        summary = analysis['summary']
        report.append("📊 SUMMARY STATISTICS")
        report.append(f"Total Feedback Received: {summary['total_feedback']}")
        report.append(f"Average Quality Score: {summary['avg_quality_score']}/5.0")
        report.append("")
        
        report.append("Quality Distribution:")
        for rating, count in summary['quality_distribution'].items():
            percentage = (count / summary['total_feedback']) * 100
            report.append(f"  {rating}: {count} ({percentage:.1f}%)")
        report.append("")
        
        # Quality Patterns
        patterns = analysis['quality_patterns']
        report.append("📈 QUALITY TRENDS")
        report.append(f"Recent Week Average: {patterns['recent_week_avg']}/5.0")
        report.append(f"Historical Average: {patterns['historical_avg']}/5.0")
        report.append(f"Trend: {patterns['trend'].upper()}")
        report.append(f"Improvement Rate: {patterns['improvement_rate']:+.2f}")
        report.append("")
        
        # Category Issues
        categories = analysis['category_insights']
        if categories:
            report.append("🎯 CATEGORY ANALYSIS")
            for category, data in sorted(categories.items(), key=lambda x: x[1]['mention_count'], reverse=True):
                report.append(f"  {category}: {data['mention_count']} mentions (avg quality: {data['avg_quality_when_mentioned']})")
            report.append("")
        
        # Improvement Opportunities
        opportunities = analysis['improvement_opportunities']
        if opportunities:
            report.append("🚀 IMPROVEMENT OPPORTUNITIES")
            for i, opp in enumerate(opportunities, 1):
                report.append(f"{i}. [{opp['priority']}] {opp['issue']}")
                report.append(f"   Impact: {opp['impact']}")
                report.append(f"   Recommendation: {opp['recommendation']}")
                report.append("")
        
        return "\n".join(report)

def main():
    """Main function for command-line usage"""
    analyzer = FeedbackAnalyzer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # Output as JSON
        analysis = analyzer.analyze_feedback_patterns()
        print(json.dumps(analysis, indent=2))
    else:
        # Output as readable report
        report = analyzer.generate_report()
        print(report)

if __name__ == "__main__":
    main()