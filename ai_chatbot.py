"""
AI Chatbot service using OpenAI API for hotel management insights
"""
import os
import sqlite3
import datetime
import json
from typing import Dict, Any, List
import openai
from dotenv import load_dotenv

load_dotenv()

class HotelAIChatbot:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.a4f.co/v1')
        )
        self.db_name = 'multi_hotel.db'
    
    def get_hotel_analytics(self, hotel_id: int) -> Dict[str, Any]:
        """Get comprehensive hotel analytics data"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        week_start = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        month_start = datetime.datetime.now().replace(day=1).strftime("%Y-%m-%d")
        
        analytics = {}
        
        try:
            # Hotel basic info
            cursor.execute('SELECT name FROM hotels WHERE id = ?', (hotel_id,))
            analytics['hotel_name'] = cursor.fetchone()[0]
            
            # Total rooms
            cursor.execute('SELECT COUNT(*) FROM rooms WHERE hotel_id = ? AND is_active = 1', (hotel_id,))
            analytics['total_rooms'] = cursor.fetchone()[0]
            
            # Today's check-ins
            cursor.execute('''
                SELECT COUNT(*) FROM bookings 
                WHERE hotel_id = ? AND check_in_date = ? AND booking_status = 'confirmed'
            ''', (hotel_id, today))
            analytics['today_checkins'] = cursor.fetchone()[0]
            
            # Today's check-outs
            cursor.execute('''
                SELECT COUNT(*) FROM bookings 
                WHERE hotel_id = ? AND check_out_date = ? AND booking_status = 'confirmed'
            ''', (hotel_id, today))
            analytics['today_checkouts'] = cursor.fetchone()[0]
            
            # Current occupancy
            cursor.execute('''
                SELECT COUNT(DISTINCT r.id)
                FROM rooms r
                JOIN bookings b ON r.id = b.room_id
                WHERE r.hotel_id = ? AND b.booking_status = 'confirmed'
                AND b.check_in_date <= ? AND b.check_out_date > ?
            ''', (hotel_id, today, today))
            analytics['occupied_rooms'] = cursor.fetchone()[0]
            
            # Daily revenue
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) FROM bookings 
                WHERE hotel_id = ? AND check_in_date = ? AND booking_status = 'confirmed' AND payment_status = 'paid'
            ''', (hotel_id, today))
            analytics['today_revenue'] = cursor.fetchone()[0]
            
            # Weekly revenue
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) FROM bookings 
                WHERE hotel_id = ? AND check_in_date >= ? AND booking_status = 'confirmed' AND payment_status = 'paid'
            ''', (hotel_id, week_start))
            analytics['weekly_revenue'] = cursor.fetchone()[0]
            
            # Monthly revenue
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) FROM bookings 
                WHERE hotel_id = ? AND check_in_date >= ? AND booking_status = 'confirmed' AND payment_status = 'paid'
            ''', (hotel_id, month_start))
            analytics['monthly_revenue'] = cursor.fetchone()[0]
            
            # Pending payments
            cursor.execute('''
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM bookings 
                WHERE hotel_id = ? AND payment_status = 'pending' AND booking_status = 'confirmed'
            ''', (hotel_id,))
            pending_data = cursor.fetchone()
            analytics['pending_payments_count'] = pending_data[0]
            analytics['pending_payments_amount'] = pending_data[1]
            
            # Room type breakdown
            cursor.execute('''
                SELECT r.room_type, COUNT(*) as total, 
                       COUNT(CASE WHEN b.check_in_date <= ? AND b.check_out_date > ? AND b.booking_status = 'confirmed' THEN 1 END) as occupied
                FROM rooms r
                LEFT JOIN bookings b ON r.id = b.room_id
                WHERE r.hotel_id = ? AND r.is_active = 1
                GROUP BY r.room_type
            ''', (today, today, hotel_id))
            analytics['room_breakdown'] = cursor.fetchall()
            
            # Upcoming bookings (next 7 days)
            next_week = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            cursor.execute('''
                SELECT COUNT(*) FROM bookings 
                WHERE hotel_id = ? AND check_in_date BETWEEN ? AND ? AND booking_status = 'confirmed'
            ''', (hotel_id, today, next_week))
            analytics['upcoming_bookings'] = cursor.fetchone()[0]
            
        except Exception as e:
            print(f"Error getting analytics: {e}")
        finally:
            conn.close()
        
        return analytics
    
    def generate_response(self, hotel_id: int, user_message: str) -> str:
        """Generate AI response based on user query and hotel data"""
        try:
            analytics = self.get_hotel_analytics(hotel_id)
            
            # Create context for the AI
            context = f"""
            You are an AI assistant for {analytics.get('hotel_name', 'the hotel')} management system. 
            
            Current hotel data:
            - Total Rooms: {analytics.get('total_rooms', 0)}
            - Occupied Rooms: {analytics.get('occupied_rooms', 0)}
            - Available Rooms: {analytics.get('total_rooms', 0) - analytics.get('occupied_rooms', 0)}
            - Occupancy Rate: {(analytics.get('occupied_rooms', 0) / max(analytics.get('total_rooms', 1), 1) * 100):.1f}%
            - Today's Check-ins: {analytics.get('today_checkins', 0)}
            - Today's Check-outs: {analytics.get('today_checkouts', 0)}
            - Today's Revenue: ${analytics.get('today_revenue', 0):.2f}
            - Weekly Revenue: ${analytics.get('weekly_revenue', 0):.2f}
            - Monthly Revenue: ${analytics.get('monthly_revenue', 0):.2f}
            - Pending Payments: {analytics.get('pending_payments_count', 0)} bookings (${analytics.get('pending_payments_amount', 0):.2f})
            - Upcoming Bookings (next 7 days): {analytics.get('upcoming_bookings', 0)}
            
            Room breakdown by type:
            {self._format_room_breakdown(analytics.get('room_breakdown', []))}
            
            Provide helpful, concise responses about hotel operations, analytics, and insights.
            Use emojis appropriately and format numbers clearly.
            """
            
            response = self.client.chat.completions.create(
                model="provider-3/gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I'm sorry, I'm having trouble accessing the hotel data right now. Error: {str(e)}"
    
    def _format_room_breakdown(self, room_breakdown: List) -> str:
        """Format room breakdown data for context"""
        if not room_breakdown:
            return "No room data available"
        
        formatted = []
        for room_type, total, occupied in room_breakdown:
            available = total - occupied
            occupancy_rate = (occupied / total * 100) if total > 0 else 0
            formatted.append(f"- {room_type}: {occupied}/{total} occupied ({occupancy_rate:.1f}% occupancy)")
        
        return "\n".join(formatted)
    
    def get_quick_insights(self, hotel_id: int) -> Dict[str, str]:
        """Get pre-formatted quick insights"""
        analytics = self.get_hotel_analytics(hotel_id)
        
        insights = {
            "occupancy": f"🏨 Current occupancy: {analytics.get('occupied_rooms', 0)}/{analytics.get('total_rooms', 0)} rooms ({(analytics.get('occupied_rooms', 0) / max(analytics.get('total_rooms', 1), 1) * 100):.1f}%)",
            "today_activity": f"📅 Today: {analytics.get('today_checkins', 0)} check-ins, {analytics.get('today_checkouts', 0)} check-outs",
            "revenue": f"💰 Revenue - Today: ${analytics.get('today_revenue', 0):.2f}, This month: ${analytics.get('monthly_revenue', 0):.2f}",
            "pending": f"⏳ {analytics.get('pending_payments_count', 0)} pending payments (${analytics.get('pending_payments_amount', 0):.2f})"
        }
        
        return insights