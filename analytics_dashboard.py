# analytics_dashboard.py: لوحة تحكم متقدمة للتحليلات
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import plot
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from database import get_analytics, Session, Conversation, Analytics
import io
import base64

logging.basicConfig(level=logging.INFO, filename='logs/chatbot.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    def __init__(self):
        """تهيئة لوحة التحكم"""
        self.session = Session()
        self.setup_plotting()
    
    def setup_plotting(self):
        """إعداد مكتبات الرسم البياني"""
        try:
            # محاولة استخدام أحدث ستايل
            plt.style.use('seaborn-v0_8')
        except:
            try:
                plt.style.use('seaborn')
            except:
                plt.style.use('default')
        try:
            sns.set_palette("husl")
        except:
            pass
        
    def get_conversation_analytics(self, days: int = 30) -> Dict[str, Any]:
        """الحصول على تحليلات المحادثات"""
        try:
            # استعلام البيانات
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            conversations = self.session.query(Conversation).filter(
                Conversation.timestamp >= start_date,
                Conversation.timestamp <= end_date
            ).all()
            
            if not conversations:
                return self._empty_analytics()
            
            # تحويل إلى DataFrame
            data = []
            for conv in conversations:
                data.append({
                    'user_id': conv.user_id,
                    'message': conv.message,
                    'response': conv.response,
                    'intent': conv.intent,
                    'sentiment': conv.sentiment,
                    'confidence': conv.confidence,
                    'timestamp': conv.timestamp
                })
            
            df = pd.DataFrame(data)
            
            # التحليلات الأساسية
            total_conversations = len(df)
            unique_users = df['user_id'].nunique()
            avg_confidence = df['confidence'].mean()
            
            # تحليل المشاعر
            sentiment_counts = df['sentiment'].value_counts()
            sentiment_distribution = sentiment_counts.to_dict()
            
            # تحليل النوايا
            intent_counts = df['intent'].value_counts()
            intent_distribution = intent_counts.to_dict()
            
            # تحليل الوقت - معالجة أنواع timestamp المختلفة
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])  # حذف القيم الفارغة
            
            if len(df) == 0:
                return self._empty_analytics()
            
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.day_name()
            df['date'] = df['timestamp'].dt.date
            
            hourly_activity = df.groupby('hour').size().to_dict()
            daily_activity = df.groupby('day_of_week').size().to_dict()
            date_activity = df.groupby('date').size().to_dict()
            
            # المستخدمون الأكثر نشاطاً
            top_users = df['user_id'].value_counts().head(10).to_dict()
            
            # طول الرسائل - معالجة القيم الفارغة
            df['message_length'] = df['message'].astype(str).str.len()
            df['response_length'] = df['response'].astype(str).str.len()
            
            avg_message_length = df['message_length'].mean()
            avg_response_length = df['response_length'].mean()
            
            return {
                'total_conversations': total_conversations,
                'unique_users': unique_users,
                'avg_confidence': float(avg_confidence) if not pd.isna(avg_confidence) else 0.0,
                'sentiment_distribution': sentiment_distribution,
                'intent_distribution': intent_distribution,
                'hourly_activity': hourly_activity,
                'daily_activity': daily_activity,
                'date_activity': {str(k): v for k, v in date_activity.items()},
                'top_users': top_users,
                'avg_message_length': float(avg_message_length) if not pd.isna(avg_message_length) else 0.0,
                'avg_response_length': float(avg_response_length) if not pd.isna(avg_response_length) else 0.0,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error in get_conversation_analytics: {e}")
            return self._empty_analytics()
    
    def _empty_analytics(self) -> Dict[str, Any]:
        """إرجاع تحليلات فارغة"""
        return {
            'total_conversations': 0,
            'unique_users': 0,
            'avg_confidence': 0.0,
            'sentiment_distribution': {},
            'intent_distribution': {},
            'hourly_activity': {},
            'daily_activity': {},
            'date_activity': {},
            'top_users': {},
            'avg_message_length': 0.0,
            'avg_response_length': 0.0,
            'period_days': 0
        }
    
    def create_sentiment_chart(self, analytics: Dict[str, Any]) -> str:
        """إنشاء مخطط توزيع المشاعر"""
        try:
            sentiment_data = analytics.get('sentiment_distribution', {})
            if not sentiment_data:
                return self._create_empty_chart()
            
            # إنشاء مخطط دائري
            fig = go.Figure(data=[go.Pie(
                labels=list(sentiment_data.keys()),
                values=list(sentiment_data.values()),
                hole=0.3
            )])
            
            fig.update_layout(
                title="توزيع المشاعر في المحادثات",
                font=dict(size=14),
                showlegend=True
            )
            
            return plot(fig, output_type='div', include_plotlyjs=False)
            
        except Exception as e:
            logger.error(f"Error creating sentiment chart: {e}")
            return self._create_empty_chart()
    
    def create_activity_chart(self, analytics: Dict[str, Any]) -> str:
        """إنشاء مخطط النشاط اليومي"""
        try:
            hourly_data = analytics.get('hourly_activity', {})
            if not hourly_data:
                return self._create_empty_chart()
            
            hours = list(range(24))
            values = [hourly_data.get(hour, 0) for hour in hours]
            
            fig = go.Figure(data=[go.Bar(
                x=hours,
                y=values,
                marker_color='lightblue'
            )])
            
            fig.update_layout(
                title="النشاط حسب الساعة",
                xaxis_title="الساعة",
                yaxis_title="عدد المحادثات",
                font=dict(size=14)
            )
            
            return plot(fig, output_type='div', include_plotlyjs=False)
            
        except Exception as e:
            logger.error(f"Error creating activity chart: {e}")
            return self._create_empty_chart()
    
    def create_user_activity_chart(self, analytics: Dict[str, Any]) -> str:
        """إنشاء مخطط نشاط المستخدمين"""
        try:
            top_users = analytics.get('top_users', {})
            if not top_users:
                return self._create_empty_chart()
            
            users = list(top_users.keys())[:10]  # أفضل 10 مستخدمين
            values = list(top_users.values())[:10]
            
            fig = go.Figure(data=[go.Bar(
                x=users,
                y=values,
                marker_color='lightgreen'
            )])
            
            fig.update_layout(
                title="أكثر المستخدمين نشاطاً",
                xaxis_title="المستخدم",
                yaxis_title="عدد المحادثات",
                font=dict(size=14),
                xaxis_tickangle=-45
            )
            
            return plot(fig, output_type='div', include_plotlyjs=False)
            
        except Exception as e:
            logger.error(f"Error creating user activity chart: {e}")
            return self._create_empty_chart()
    
    def create_intent_chart(self, analytics: Dict[str, Any]) -> str:
        """إنشاء مخطط توزيع النوايا"""
        try:
            intent_data = analytics.get('intent_distribution', {})
            if not intent_data:
                return self._create_empty_chart()
            
            fig = go.Figure(data=[go.Pie(
                labels=list(intent_data.keys()),
                values=list(intent_data.values()),
                hole=0.3
            )])
            
            fig.update_layout(
                title="توزيع النوايا في المحادثات",
                font=dict(size=14),
                showlegend=True
            )
            
            return plot(fig, output_type='div', include_plotlyjs=False)
            
        except Exception as e:
            logger.error(f"Error creating intent chart: {e}")
            return self._create_empty_chart()
    
    def create_trend_chart(self, analytics: Dict[str, Any]) -> str:
        """إنشاء مخطط الاتجاهات الزمنية"""
        try:
            date_data = analytics.get('date_activity', {})
            if not date_data:
                return self._create_empty_chart()
            
            dates = sorted(date_data.keys())
            values = [date_data[date] for date in dates]
            
            fig = go.Figure(data=[go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            )])
            
            fig.update_layout(
                title="اتجاه المحادثات عبر الوقت",
                xaxis_title="التاريخ",
                yaxis_title="عدد المحادثات",
                font=dict(size=14)
            )
            
            return plot(fig, output_type='div', include_plotlyjs=False)
            
        except Exception as e:
            logger.error(f"Error creating trend chart: {e}")
            return self._create_empty_chart()
    
    def _create_empty_chart(self) -> str:
        """إنشاء مخطط فارغ"""
        fig = go.Figure()
        fig.add_annotation(
            text="لا توجد بيانات متاحة",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return plot(fig, output_type='div', include_plotlyjs=False)
    
    def generate_report(self, days: int = 30) -> Dict[str, Any]:
        """توليد تقرير شامل"""
        try:
            analytics = self.get_conversation_analytics(days)
            
            # إنشاء المخططات
            sentiment_chart = self.create_sentiment_chart(analytics)
            activity_chart = self.create_activity_chart(analytics)
            user_chart = self.create_user_activity_chart(analytics)
            intent_chart = self.create_intent_chart(analytics)
            trend_chart = self.create_trend_chart(analytics)
            
            # حساب المؤشرات الرئيسية
            total_conversations = analytics.get('total_conversations', 0)
            unique_users = analytics.get('unique_users', 0)
            avg_confidence = analytics.get('avg_confidence', 0.0)
            
            # حساب معدل النمو
            current_period = analytics.get('date_activity', {})
            if len(current_period) >= 2:
                dates = sorted(current_period.keys())
                recent_avg = np.mean(list(current_period.values())[-7:])  # آخر 7 أيام
                older_avg = np.mean(list(current_period.values())[:-7]) if len(current_period) > 7 else recent_avg
                growth_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            else:
                growth_rate = 0
            
            return {
                'analytics': analytics,
                'charts': {
                    'sentiment': sentiment_chart,
                    'activity': activity_chart,
                    'users': user_chart,
                    'intent': intent_chart,
                    'trend': trend_chart
                },
                'kpis': {
                    'total_conversations': total_conversations,
                    'unique_users': unique_users,
                    'avg_confidence': round(avg_confidence, 2),
                    'growth_rate': round(growth_rate, 2),
                    'avg_message_length': analytics.get('avg_message_length', 0),
                    'avg_response_length': analytics.get('avg_response_length', 0)
                },
                'generated_at': datetime.now().isoformat(),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                'error': str(e),
                'analytics': self._empty_analytics(),
                'charts': {},
                'kpis': {},
                'generated_at': datetime.now().isoformat()
            }
    
    def export_data(self, format: str = 'csv', days: int = 30) -> str:
        """تصدير البيانات"""
        try:
            # الحصول على البيانات الخام من قاعدة البيانات
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            conversations = self.session.query(Conversation).filter(
                Conversation.timestamp >= start_date,
                Conversation.timestamp <= end_date
            ).all()
            
            if not conversations:
                return ""
            
            # تحويل إلى DataFrame
            data = []
            for conv in conversations:
                data.append({
                    'user_id': conv.user_id,
                    'message': conv.message,
                    'response': conv.response,
                    'intent': conv.intent,
                    'sentiment': conv.sentiment,
                    'confidence': conv.confidence,
                    'timestamp': conv.timestamp.isoformat() if hasattr(conv.timestamp, 'isoformat') else str(conv.timestamp)
                })
            
            df = pd.DataFrame(data)
            
            if format.lower() == 'csv':
                # تصدير كـ CSV
                csv_string = df.to_csv(index=False, encoding='utf-8-sig')
                return csv_string
            elif format.lower() == 'json':
                # تصدير كـ JSON
                return json.dumps(data, ensure_ascii=False, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return ""
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات فورية"""
        try:
            # آخر ساعة
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_conversations = self.session.query(Conversation).filter(
                Conversation.timestamp >= one_hour_ago
            ).count()
            
            # آخر 24 ساعة
            one_day_ago = datetime.now() - timedelta(days=1)
            daily_conversations = self.session.query(Conversation).filter(
                Conversation.timestamp >= one_day_ago
            ).count()
            
            # المستخدمون النشطون الآن (آخر 10 دقائق)
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)
            active_users = self.session.query(Conversation.user_id).filter(
                Conversation.timestamp >= ten_minutes_ago
            ).distinct().count()
            
            return {
                'conversations_last_hour': recent_conversations,
                'conversations_last_24h': daily_conversations,
                'active_users_now': active_users,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time stats: {e}")
            return {
                'conversations_last_hour': 0,
                'conversations_last_24h': 0,
                'active_users_now': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def close(self):
        """إغلاق الجلسة بشكل صريح"""
        if hasattr(self, 'session'):
            try:
                self.session.close()
            except:
                pass
    
    def __del__(self):
        """إغلاق الجلسة"""
        self.close()
    
    def __enter__(self):
        """دعم context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """إغلاق عند الخروج من context"""
        self.close()
