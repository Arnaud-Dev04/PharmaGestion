"""
Report Routes - Endpoints for file exports (Excel/PDF).
"""

from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_local_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.services import report_service

router = APIRouter()


@router.get(
    "/stock/pdf",
    summary="Download stock report (PDF)"
)
async def download_stock_pdf(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Generate and download current stock status as PDF.
    """
    pdf_file = report_service.generate_stock_pdf(db)
    
    headers = {
        'Content-Disposition': f'attachment; filename="stock_report_{date.today()}.pdf"'
    }
    
    return StreamingResponse(
        pdf_file,
        media_type='application/pdf',
        headers=headers
    )


@router.get(
    "/stock/excel",
    summary="Download stock report (Excel)"
)
async def download_stock_excel(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Generate and download current stock status as Excel.
    """
    excel_file = report_service.generate_stock_excel(db)
    
    headers = {
        'Content-Disposition': f'attachment; filename="stock_report_{date.today()}.xlsx"'
    }
    
    return StreamingResponse(
        excel_file,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers=headers
    )


@router.get(
    "/stock/word",
    summary="Download stock report (Word)"
)
async def download_stock_word(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Generate and download current stock status as Word (doc).
    """
    word_file = report_service.generate_stock_word(db)
    
    headers = {
        'Content-Disposition': f'attachment; filename="stock_report_{date.today()}.doc"'
    }
    
    return StreamingResponse(
        word_file,
        media_type='application/msword',
        headers=headers
    )


@router.get(
    "/sales/pdf",
    summary="Download sales report (PDF)"
)
async def download_sales_pdf(
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Generate and download sales history as PDF.
    Requires start_date and end_date.
    """
    pdf_file = report_service.generate_sales_pdf(db, start_date, end_date)
    
    headers = {
        'Content-Disposition': f'attachment; filename="sales_report_{start_date}_{end_date}.pdf"'
    }
    
    return StreamingResponse(
        pdf_file,
        media_type='application/pdf',
        headers=headers
    )


@router.get(
    "/sales/excel",
    summary="Download sales report (Excel)"
)
async def download_sales_excel(
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Generate and download sales history as Excel.
    """
    excel_file = report_service.generate_sales_excel(db, start_date, end_date)
    
    headers = {
        'Content-Disposition': f'attachment; filename="sales_report_{start_date}_{end_date}.xlsx"'
    }
    
    return StreamingResponse(
        excel_file,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers=headers
    )


@router.get(
    "/sales/word",
    summary="Download sales report (Word)"
)
async def download_sales_word(
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Generate and download sales history as Word.
    """
    word_file = report_service.generate_sales_word(db, start_date, end_date)
    
    headers = {
        'Content-Disposition': f'attachment; filename="sales_report_{start_date}_{end_date}.doc"'
    }
    
    return StreamingResponse(
        word_file,
        media_type='application/msword',
        headers=headers
    )


@router.get(
    "/financial/pdf",
    summary="Download financial summary (PDF)"
)
async def download_financial_pdf(
    start_date: date = Query(None, description="Start date for period filter"),
    end_date: date = Query(None, description="End date for period filter"),
    period: str = "month",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_local_db)
):
    """
    Generate and download a professional financial PDF report.
    Optionally filter by date range.
    """
    pdf_file = report_service.generate_financial_pdf(
        db, 
        start_date=start_date,
        end_date=end_date,
        period_label=period
    )
    
    headers = {
        'Content-Disposition': f'attachment; filename="financial_report_{date.today()}.pdf"'
    }
    
    return StreamingResponse(
        pdf_file,
        media_type='application/pdf',
        headers=headers
    )
