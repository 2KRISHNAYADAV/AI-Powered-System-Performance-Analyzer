import csv
import datetime
import os

class ReportGenerator:
    @staticmethod
    def export_csv(filepath, data_state):
        try:
            with open(filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["SystemHero Comprehensive Report"])
                writer.writerow(["Generated At", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow([])
                
                writer.writerow(["--- core metrics ---"])
                writer.writerow(["CPU Total %", "RAM Total %", "Disk Usage %", "Focus Score"])
                writer.writerow([
                    data_state.get('cpu_total', 0),
                    data_state.get('ram_total', 0),
                    data_state.get('disk_usage', 0),
                    data_state.get('focus_score', 100)
                ])
                writer.writerow([])
                
                writer.writerow(["--- top processes ---"])
                writer.writerow(["PID", "Name", "CPU %", "RAM MB"])
                procs = data_state.get('processes', [])
                for p in procs[:15]:
                    writer.writerow([p.get('pid'), p.get('name'), p.get('cpu', 0), p.get('ram_mb', 0)])
            
            return True, f"Report saved to {filepath}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def export_html(filepath, data_state):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html = f"""
        <html>
        <head>
            <title>SystemHero Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }}
                h1 {{ color: #38bdf8; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #334155; padding: 10px; text-align: left; }}
                th {{ background: #1e293b; color: #94a3b8; }}
                .card {{ background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>SystemHero Interactive Report</h1>
            <p>Generated: {ts}</p>
            <div class="card">
                <h3>Vitals</h3>
                <p><b>CPU:</b> {data_state.get('cpu_total', 0)}% &nbsp;|&nbsp; <b>RAM:</b> {data_state.get('ram_total', 0)}%</p>
                <p><b>Disk:</b> {data_state.get('disk_usage', 0)}% &nbsp;|&nbsp; <b>Focus:</b> {data_state.get('focus_score', 100)}/100</p>
            </div>
            <h3>Top Processes</h3>
            <table>
                <tr><th>PID</th><th>Name</th><th>CPU %</th><th>RAM MB</th></tr>
        """
        for p in data_state.get('processes', [])[:15]:
            html += f"<tr><td>{p.get('pid')}</td><td>{p.get('name')}</td><td>{p.get('cpu', 0):.1f}</td><td>{p.get('ram_mb', 0):.1f}</td></tr>"
            
        html += """
            </table>
        </body>
        </html>
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            return True, f"Report saved to {filepath}"
        except Exception as e:
            return False, str(e)
