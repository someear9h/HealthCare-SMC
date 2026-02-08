"""Professional PDF report generation service for Solapur Municipal Corporation.

Generates executive health system reports with system architecture and analytics insights.
Uses fpdf2 for lightweight, pure-Python PDF generation.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from fpdf import FPDF

from repositories.status_repository import StatusRepository
from repositories.ambulance_repository import AmbulanceRepository
from services.prediction_service import PredictionService
from services.ward_risk_service import WardRiskService
from services.ambulance_service import AmbulanceService


class SolapurHealthReportPDF(FPDF):
    """Custom PDF class for SMC Health Report with headers and footers."""

    def __init__(self):
        """Initialize PDF with custom settings."""
        super().__init__(orientation='P', unit='mm', format='A4')
        self.title_font_size = 16
        self.heading_font_size = 12
        self.normal_font_size = 10
        self.small_font_size = 8

    def header(self):
        """Add header to each page."""
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'Solapur Municipal Corporation', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 7, 'Health System Executive Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, title: str):
        """Add section title with formatting."""
        self.set_font('Helvetica', 'B', self.heading_font_size)
        self.set_text_color(25, 70, 130)  # Dark blue
        self.cell(0, 10, title, 0, 1)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def add_metric(self, label: str, value: Any, unit: str = ''):
        """Add a metric row (label: value)."""
        self.set_font('Helvetica', '', self.normal_font_size)
        metric_str = f'{label}: '
        self.cell(100, 8, metric_str)
        self.set_font('Helvetica', 'B', self.normal_font_size)
        self.cell(0, 8, f'{value} {unit}', 0, 1)

    def add_table(self, headers: list, rows: list, col_widths: Optional[list] = None):
        """Add a table to the PDF."""
        if not col_widths:
            col_widths = [190 / len(headers)] * len(headers)

        # Header row
        self.set_font('Helvetica', 'B', self.normal_font_size)
        self.set_fill_color(200, 220, 255)
        for header, width in zip(headers, col_widths):
            self.cell(width, 8, header, 1, 0, 'C', fill=True)
        self.ln()

        # Data rows
        self.set_font('Helvetica', '', self.small_font_size)
        for row in rows:
            for cell, width in zip(row, col_widths):
                self.cell(width, 7, str(cell), 1, 0, 'L')
            self.ln()
        self.ln(2)


class ReportService:
    """Service for generating PDF reports using city analytics data.

    Leverages existing repositories and services to compile actionable intelligence
    for Municipal Commissioners and Health Officers.
    """

    def __init__(self, db: Session):
        """Initialize service with DB session.

        Args:
            db: SQLAlchemy session.
        """
        self.db = db
        self.status_repo = StatusRepository(db)
        self.ambulance_repo = AmbulanceRepository(db)
        self.prediction_service = PredictionService(db)
        self.ward_risk_service = WardRiskService(db)
        self.ambulance_service = AmbulanceService(db)

    def generate_summary_pdf(self) -> bytes:
        """Generate comprehensive health system executive report.

        Creates a professional PDF with:
        - City-wide resource summary
        - Facility crisis analysis
        - Ward-level risk assessment
        - Ambulance fleet status
        - Risk mitigation recommendations

        Returns:
            PDF as bytes (ready for download).
        """
        pdf = SolapurHealthReportPDF()
        pdf.add_page()

        # ==== EXECUTIVE SUMMARY ====
        pdf.section_title('Executive Summary')
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(
            0, 5,
            'This report provides a comprehensive overview of Solapur Municipal Corporation\'s '
            'health system status. It includes resource availability, facility utilization '
            'forecasts, and ward-level risk assessments to support operational decision-making.'
        )
        pdf.ln(3)

        # ==== CITY TOTALS ====
        pdf.section_title('City-Wide Resource Status')
        totals = self.status_repo.get_city_totals()
        
        # Create metrics grid
        metrics = [
            ('Total Beds Available', totals.get('total_beds', 0), 'beds'),
            ('ICU Units Available', totals.get('total_icu', 0), 'units'),
            ('Ventilators Available', totals.get('total_ventilators', 0), 'units'),
            ('Oxygen Units Available', totals.get('total_oxygen', 0), 'units'),
        ]
        
        for label, value, unit in metrics:
            pdf.add_metric(label, value, unit)
        pdf.ln(2)

        # ==== FACILITY CRISIS ANALYSIS ====
        pdf.section_title('Facility Crisis Analysis')
        try:
            predictions = self.prediction_service.predict_all_facilities()
            crisis_facilities = [
                p for p in predictions.get('predictions', [])
                if p.get('crisis_likely', False)
            ]
            
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 8, f'Facilities in Crisis: {len(crisis_facilities)} / {len(predictions.get("predictions", []))}', 0, 1)
            pdf.ln(2)
            
            if crisis_facilities:
                headers = ['Facility ID', 'Projected 24h Cases', 'Beds Remaining (hrs)']
                rows = [
                    [
                        p.get('facility_id', 'N/A')[:20],
                        p.get('projected_24h_admissions', '--'),
                        f"{p.get('beds_remaining_hours', float('inf')):.1f}"
                    ]
                    for p in crisis_facilities[:5]  # Top 5 crisis facilities
                ]
                pdf.add_table(headers, rows, col_widths=[60, 60, 70])
        except Exception as e:
            pdf.set_font('Helvetica', '', 9)
            pdf.cell(0, 8, f'[Unable to process predictions: {str(e)[:50]}]', 0, 1)
            pdf.ln(2)

        # ==== WARD RISK ASSESSMENT ====
        pdf.section_title('Ward-Level Risk Assessment')
        try:
            ward_risks = self.ward_risk_service.get_all_wards_risk()
            wards_data = ward_risks.get('wards', [])
            
            # Risk distribution summary
            risk_counts = {
                'CRITICAL': len([w for w in wards_data if w.get('risk_level') == 'CRITICAL']),
                'HIGH': len([w for w in wards_data if w.get('risk_level') == 'HIGH']),
                'MEDIUM': len([w for w in wards_data if w.get('risk_level') == 'MEDIUM']),
                'LOW': len([w for w in wards_data if w.get('risk_level') == 'LOW']),
            }
            
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 8, f'Total Wards: {len(wards_data)}', 0, 1)
            for risk_level, count in risk_counts.items():
                pdf.add_metric(f'{risk_level} Risk Wards', count, '')
            pdf.ln(2)
            
            # Top critical wards table
            critical_high = [w for w in wards_data if w.get('risk_level') in ['CRITICAL', 'HIGH']]
            if critical_high:
                headers = ['Ward', 'Risk Level', 'Risk Score', 'ICU Pressure']
                rows = [
                    [
                        w.get('ward', 'N/A')[:15],
                        w.get('risk_level', 'N/A'),
                        f"{w.get('risk_score', 0):.1f}",
                        f"{w.get('icu_pressure', 0):.1f}%"
                    ]
                    for w in critical_high[:8]
                ]
                pdf.add_table(headers, rows, col_widths=[45, 35, 50, 60])
        except Exception as e:
            pdf.set_font('Helvetica', '', 9)
            pdf.cell(0, 8, f'[Unable to process ward risks: {str(e)[:50]}]', 0, 1)
            pdf.ln(2)

        # ==== AMBULANCE FLEET STATUS ====
        pdf.section_title('Ambulance Fleet Status')
        try:
            all_ambulances = self.ambulance_repo.get_all()
            if all_ambulances:
                status_counts = {}
                for amb in all_ambulances:
                    status = amb.status if hasattr(amb, 'status') else 'AVAILABLE'
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                pdf.set_font('Helvetica', '', 10)
                pdf.cell(0, 8, f'Total Ambulances: {len(all_ambulances)}', 0, 1)
                for status, count in status_counts.items():
                    pdf.add_metric(f'{status} Ambulances', count, '')
                pdf.ln(2)
            else:
                pdf.set_font('Helvetica', '', 10)
                pdf.cell(0, 8, 'No ambulance data available.', 0, 1)
        except Exception as e:
            pdf.set_font('Helvetica', '', 9)
            pdf.cell(0, 8, f'[Unable to process ambulances: {str(e)[:50]}]', 0, 1)
            pdf.ln(2)

        # ==== NEW PAGE: RECOMMENDATIONS ====
        pdf.add_page()
        pdf.section_title('Risk Mitigation Recommendations')
        pdf.set_font('Helvetica', '', 10)
        
        recommendations = [
            '- Prioritize resource allocation to facilities with crisis projections within 24 hours',
            '- Deploy additional ambulances to CRITICAL and HIGH risk wards for rapid response',
            '- Coordinate bed transfers between stable facilities and those in crisis',
            '- Activate surge capacity protocols if ICU pressure exceeds 80%',
            '- Implement 6-hourly status monitoring for facilities trending toward crisis',
            '- Maintain oxygen and ventilator inventory margins of 15% above peak consumption',
        ]
        
        for rec in recommendations:
            pdf.multi_cell(0, 6, rec)
            pdf.ln(1)

        # ==== FOOTER NOTES ====
        pdf.ln(5)
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(
            0, 4,
            'This report is generated automatically from live health system data. '
            'All metrics are based on latest facility submissions as of report generation time. '
            'For detailed facility analysis, consult the interactive dashboard.'
        )

        # Return PDF as bytes
        return pdf.output()

    def generate_facility_pdf(self, facility_id: str) -> bytes:
        """Generate detailed report for a specific facility.

        Args:
            facility_id: Target facility.

        Returns:
            PDF as bytes.
        """
        pdf = SolapurHealthReportPDF()
        pdf.add_page()

        # Title
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, f'Facility Report: {facility_id}', 0, 1)
        pdf.ln(3)

        # Facility Status
        pdf.section_title('Current Status')
        latest_status = self.status_repo.get_latest_by_facility(facility_id)
        if latest_status:
            metrics = [
                ('Beds Available', latest_status.beds_available, 'beds'),
                ('ICU Available', latest_status.icu_available, 'units'),
                ('Ventilators', latest_status.ventilators_available, 'units'),
                ('Oxygen Units', latest_status.oxygen_units_available, 'units'),
                ('Medicine Stock', latest_status.medicine_stock_status, ''),
            ]
            for label, value, unit in metrics:
                pdf.add_metric(label, value, unit)
        pdf.ln(2)

        # Bed Demand Prediction
        pdf.section_title('Bed Demand Forecast')
        try:
            prediction = self.prediction_service.predict_bed_demand(facility_id)
            pdf.add_metric('Avg Admission Rate', f"{prediction.get('avg_admission_rate', 0):.2f}", 'cases/hour')
            pdf.add_metric('24h Projection', prediction.get('projected_24h_admissions', 0), 'cases')
            pdf.add_metric('Crisis Likely', 'Yes' if prediction.get('crisis_likely') else 'No', '')
        except Exception as e:
            pdf.set_font('Helvetica', '', 9)
            pdf.cell(0, 8, f'[Prediction unavailable: {str(e)[:40]}]', 0, 1)

        return pdf.output()
