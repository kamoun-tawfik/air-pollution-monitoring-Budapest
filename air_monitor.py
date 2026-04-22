import requests
import csv
import os
from datetime import datetime
import time

API_KEY = "67ec64d4bb792676559a57ec64c7a080"  

# Budapest coordinates
LATITUDE = 47.4979   # Budapest
LONGITUDE = 19.0402  # Budapest
CITY_NAME = "Budapest"

# Collection settings
NUM_READINGS = 20      # Number of readings to collect
INTERVAL_SECONDS = 5   # Wait 5 seconds between readings

# ============ MAIN MONITOR CLASS ============
class AirQualityMonitor:
    def __init__(self):
        self.lat = LATITUDE
        self.lon = LONGITUDE
        self.city = CITY_NAME
        self.api_key = API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        self.data_file = "pollution_data.csv"
        
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'city', 'pm2_5', 'pm10', 'no2', 'o3', 'so2', 'co', 'aqi'])
            print(f"✓ Created new data file: {self.data_file}")
        else:
            # Count existing readings
            with open(self.data_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                row_count = sum(1 for row in reader) - 1
                if row_count > 0:
                    print(f"✓ Found existing file with {row_count} readings")
    
    def fetch_data(self):
        """Get air pollution data from API"""
        url = f"{self.base_url}?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract pollution measurements
            components = data['list'][0]['components']
            
            result = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'city': self.city,
                'pm2_5': round(components.get('pm2_5', 0), 1),
                'pm10': round(components.get('pm10', 0), 1),
                'no2': round(components.get('no2', 0), 1),
                'o3': round(components.get('o3', 0), 1),
                'so2': round(components.get('so2', 0), 1),
                'co': round(components.get('co', 0), 1),
                'aqi': data['list'][0]['main']['aqi']
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"   ✗ API Error: {e}")
            return None
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return None
    
    def save_data(self, data):
        """Save to CSV file"""
        if data is None:
            return False
        
        with open(self.data_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data['timestamp'],
                data['city'],
                data['pm2_5'],
                data['pm10'],
                data['no2'],
                data['o3'],
                data['so2'],
                data['co'],
                data['aqi']
            ])
        return True
    
    def check_alerts(self, data):
        """Check if pollution exceeds safe limits (WHO guidelines)"""
        if data is None:
            return []
        
        alerts = []
        
        # WHO safe limits
        thresholds = {
            'pm2_5': {'limit': 15, 'name': 'PM2.5', 'current': data['pm2_5']},
            'pm10': {'limit': 45, 'name': 'PM10', 'current': data['pm10']},
            'no2': {'limit': 25, 'name': 'NO₂', 'current': data['no2']},
            'o3': {'limit': 100, 'name': 'O₃', 'current': data['o3']}
        }
        
        for key, info in thresholds.items():
            if info['current'] > info['limit']:
                alerts.append(f"   ⚠️ WARNING: {info['name']} is {info['current']} (WHO limit: {info['limit']})")
        
        # AQI warnings
        aqi_names = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        if data['aqi'] >= 4:
            alerts.append(f"   ⚠️ WARNING: Air Quality is {aqi_names.get(data['aqi'], 'Unknown')} (AQI: {data['aqi']})")
        
        for alert in alerts:
            print(alert)
        
        if not alerts:
            print("   ✓ Air quality within safe limits")
        
        return alerts
    
    def create_matplotlib_graphs(self):
        """Create professional graphs using Matplotlib (meets software requirement)"""
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
        except ImportError:
            print("\n❌ Matplotlib or Pandas not installed. Run: pip install matplotlib pandas")
            return None
        
        if not os.path.exists(self.data_file):
            print("\n❌ No data file found. Run data collection first.")
            return None
        
        # Load data
        df = pd.read_csv(self.data_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        if len(df) < 2:
            print("\n❌ Need at least 2 data points for graphs.")
            return None
        
        print("\n" + "="*60)
        print("📊 GENERATING MATPLOTLIB GRAPHS (Software Requirement)")
        print("="*60)
        
        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Budapest Air Quality Analysis - {self.city}', 
                     fontsize=16, fontweight='bold')
        
        # Graph 1: PM2.5 and PM10 over time
        axes[0, 0].plot(df['timestamp'], df['pm2_5'], 'ro-', label='PM2.5', linewidth=2, markersize=6)
        axes[0, 0].plot(df['timestamp'], df['pm10'], 'bo-', label='PM10', linewidth=2, markersize=6)
        axes[0, 0].axhline(y=15, color='r', linestyle='--', alpha=0.7, label='PM2.5 WHO Limit (15)')
        axes[0, 0].axhline(y=45, color='b', linestyle='--', alpha=0.7, label='PM10 WHO Limit (45)')
        axes[0, 0].set_title('Particulate Matter (PM2.5 & PM10)', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Concentration (µg/m³)')
        axes[0, 0].legend(loc='upper right')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Graph 2: NO2 and O3 over time
        axes[0, 1].plot(df['timestamp'], df['no2'], 'go-', label='NO₂', linewidth=2, markersize=6)
        axes[0, 1].plot(df['timestamp'], df['o3'], 'o-', label='O₃', linewidth=2, markersize=6, color='orange')
        axes[0, 1].axhline(y=25, color='g', linestyle='--', alpha=0.7, label='NO₂ WHO Limit (25)')
        axes[0, 1].axhline(y=100, color='orange', linestyle='--', alpha=0.7, label='O₃ WHO Limit (100)')
        axes[0, 1].set_title('Gas Pollutants (NO₂ & O₃)', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Time')
        axes[0, 1].set_ylabel('Concentration (µg/m³)')
        axes[0, 1].legend(loc='upper right')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Graph 3: Air Quality Index
        axes[1, 0].plot(df['timestamp'], df['aqi'], 'mo-', linewidth=2, markersize=8, label='AQI')
        axes[1, 0].axhline(y=3, color='orange', linestyle='--', linewidth=2, label='Moderate Threshold (3)')
        axes[1, 0].axhline(y=4, color='r', linestyle='--', linewidth=2, label='Poor Threshold (4)')
        axes[1, 0].set_title('Air Quality Index (1=Good to 5=Very Poor)', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Time')
        axes[1, 0].set_ylabel('AQI')
        axes[1, 0].set_ylim(0, 6)
        axes[1, 0].legend(loc='upper right')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Graph 4: Latest readings bar chart
        latest = df.iloc[-1]
        pollutants = ['PM2.5', 'PM10', 'NO₂', 'O₃']
        values = [latest['pm2_5'], latest['pm10'], latest['no2'], latest['o3']]
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
        bars = axes[1, 1].bar(pollutants, values, color=colors, edgecolor='black', linewidth=1.5)
        
        # Convert timestamp to string safely
        if hasattr(latest['timestamp'], 'strftime'):
            time_str = latest['timestamp'].strftime('%H:%M:%S')
        else:
            time_str = str(latest['timestamp'])[11:16] if len(str(latest['timestamp'])) > 11 else str(latest['timestamp'])
        
        axes[1, 1].set_title(f'Latest Readings - {time_str}', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Concentration (µg/m³)')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        # Adjust layout and save
        plt.tight_layout()
        
        # Save the figure with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"budapest_air_quality_{timestamp}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"✓ Matplotlib graph saved as: {filename}")
        
        # Also save as standard name for presentation
        plt.savefig("air_quality_matplotlib.png", dpi=150, bbox_inches='tight')
        print(f"✓ Graph also saved as: air_quality_matplotlib.png")
        
        # Show the plot
        plt.show()
        
        print("="*60)
        print("✓ Matplotlib graphs generated successfully!")
        print("="*60)
        
        return filename
    
    def show_summary(self):
        """Display comprehensive summary of collected data including O₃"""
        if not os.path.exists(self.data_file):
            print("\n❌ No data collected yet")
            return
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) <= 1:
            print("\n❌ No data collected yet")
            return
        
        print("\n" + "="*60)
        print("📊 DATA COLLECTION SUMMARY")
        print("="*60)
        
        # Data rows (skip header)
        data_rows = rows[1:]
        total_readings = len(data_rows)
        print(f"Total readings: {total_readings}")
        print(f"First reading: {data_rows[0][0]}")
        print(f"Last reading: {data_rows[-1][0]}")
        
        # Calculate averages for ALL pollutants including O₃
        pm25_sum = sum(float(row[2]) for row in data_rows)
        pm10_sum = sum(float(row[3]) for row in data_rows)
        no2_sum = sum(float(row[4]) for row in data_rows)
        o3_sum = sum(float(row[5]) for row in data_rows)
        
        avg_pm25 = pm25_sum / total_readings
        avg_pm10 = pm10_sum / total_readings
        avg_no2 = no2_sum / total_readings
        avg_o3 = o3_sum / total_readings
        
        print("\n📈 Average Pollution Levels:")
        print(f"   🌫️  PM2.5: {avg_pm25:.1f} µg/m³", end="")
        print(" ✓ (Within WHO limit)" if avg_pm25 <= 15 else " ⚠️ (Above WHO limit)")
            
        print(f"   🍃 PM10:  {avg_pm10:.1f} µg/m³", end="")
        print(" ✓ (Within WHO limit)" if avg_pm10 <= 45 else " ⚠️ (Above WHO limit)")
            
        print(f"   💨 NO₂:   {avg_no2:.1f} µg/m³", end="")
        print(" ✓ (Within WHO limit)" if avg_no2 <= 25 else " ⚠️ (Above WHO limit)")
            
        print(f"   🌫️  O₃:    {avg_o3:.1f} µg/m³", end="")
        print(" ✓ (Within WHO limit)" if avg_o3 <= 100 else " ⚠️ (Above WHO limit)")
        
        # Latest AQI
        latest_aqi = int(float(data_rows[-1][8]))
        aqi_names = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        aqi_colors = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "⚫"}
        
        print(f"\n🎯 Latest Air Quality Index: {aqi_colors.get(latest_aqi, '')} {latest_aqi} - {aqi_names.get(latest_aqi, 'Unknown')}")
        
        # Trend analysis
        if total_readings >= 6:
            half = total_readings // 2
            first_half_avg = sum(float(row[2]) for row in data_rows[:half]) / half
            second_half_avg = sum(float(row[2]) for row in data_rows[-half:]) / half
            
            print("\n📉 Trend Analysis (PM2.5):")
            print(f"   First {half} readings average: {first_half_avg:.1f} µg/m³")
            print(f"   Last {half} readings average: {second_half_avg:.1f} µg/m³")
            
            if second_half_avg < first_half_avg:
                print("   📈 Trend: Improving air quality ↓")
            elif second_half_avg > first_half_avg:
                print("   📉 Trend: Declining air quality ↑")
            else:
                print("   ➡️ Trend: Stable")
    
    def show_data_table(self):
        """Display data in a formatted table including O₃"""
        if not os.path.exists(self.data_file):
            return
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) <= 1:
            return
        
        print("\n" + "="*90)
        print("📋 COLLECTED DATA (All Pollutants)")
        print("="*90)
        print(f"{'Time':<12} {'PM2.5':<8} {'PM10':<8} {'NO₂':<8} {'O₃':<8} {'AQI':<10}")
        print("-"*90)
        
        data_rows = rows[1:]
        for row in data_rows[-15:]:
            time_short = row[0][11:16]
            aqi_val = int(float(row[8]))
            aqi_name = {1:"Good",2:"Fair",3:"Moderate",4:"Poor",5:"Very Poor"}.get(aqi_val, "")
            print(f"{time_short:<12} {row[2]:<8} {row[3]:<8} {row[4]:<8} {row[5]:<8} {aqi_val} ({aqi_name})")
        
        print("="*90)
    
    def collect_data(self, num_readings=None, interval_seconds=None):
        """Main collection loop"""
        num = num_readings if num_readings is not None else NUM_READINGS
        interval = interval_seconds if interval_seconds is not None else INTERVAL_SECONDS
        
        print("\n" + "="*60)
        print(f"🌍 AIR QUALITY MONITOR - {self.city}")
        print(f"📍 Coordinates: {self.lat}, {self.lon}")
        print(f"📊 Collecting {num} readings every {interval} seconds")
        print("="*60)
        
        successful_readings = 0
        
        for i in range(num):
            print(f"\n📊 Reading {i+1}/{num}")
            
            data = self.fetch_data()
            
            if data:
                if self.save_data(data):
                    successful_readings += 1
                    print(f"   ✓ PM2.5: {data['pm2_5']} | PM10: {data['pm10']} | NO₂: {data['no2']} | O₃: {data['o3']} | AQI: {data['aqi']}")
                    self.check_alerts(data)
                else:
                    print(f"   ✗ Failed to save data")
            else:
                print(f"   ✗ Failed to fetch data")
            
            if i < num - 1:
                print(f"\n   ⏳ Waiting {interval} seconds...")
                time.sleep(interval)
        
        print("\n" + "="*60)
        print(f"✅ COLLECTION COMPLETE! ({successful_readings}/{num} successful)")
        print("="*60)
        
        if successful_readings > 0:
            self.show_summary()
            self.show_data_table()
            
            # Generate Matplotlib graphs (meets software requirement)
            self.create_matplotlib_graphs()
        
        print(f"\n📁 Data saved to: {os.path.abspath(self.data_file)}")
        
        return successful_readings

# ============ RUN THE PROGRAM ============
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     AIR POLLUTION MONITORING SYSTEM v2.0         ║
    ║         Budapest Air Quality Monitor             ║
    ║    Includes: Matplotlib Graphs + Data Collection ║
    ║              Intermediate Checkpoint             ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    # Check if API key is set
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ERROR: You need to set your API key!")
        print("\n📝 INSTRUCTIONS:")
        print("1. Go to https://home.openweathermap.org/users/sign_up")
        print("2. Create a free account")
        print("3. Verify your email")
        print("4. Go to https://home.openweathermap.org/api_keys")
        print("5. Copy your API key")
        print("6. Open this file and replace 'YOUR_API_KEY_HERE' with your key")
        exit()
    
    # Check internet connection
    try:
        requests.get("https://api.openweathermap.org", timeout=5)
        print("✓ Internet connection OK")
    except:
        print("⚠️ Warning: Internet connection may be unstable")
    
    # Create monitor
    monitor = AirQualityMonitor()
    
    print(f"\n📍 Location: {CITY_NAME}")
    print(f"📡 Starting data collection...")
    print(f"\n🎯 Collecting {NUM_READINGS} readings with {INTERVAL_SECONDS} second intervals")
    print(f"⏱️  Estimated time: ~{NUM_READINGS * INTERVAL_SECONDS / 60:.1f} minutes\n")
    
    # Run collection
    monitor.collect_data()
    
    print("\n" + "="*60)
    print("🎉 PROGRAM FINISHED SUCCESSFULLY!")
    print("="*60)
    print("\n📌 NEXT STEPS:")
    print("   1. Check the Matplotlib graph that just opened")
    print("   2. Open dashboard.html to see interactive visualizations")
    print("   3. Check pollution_data.csv in Excel")
    print("   4. Screenshot air_quality_matplotlib.png for your slides")
    print("")